/**
 * useVoiceChat Hook
 * Main orchestrator hook for voice chat functionality
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { logger } from '../config/audio-config';
import { initAudioRecorder, stopAudioRecorder } from '../services/audio/audio-recorder';
import { initAudioPlayer, stopAudioPlayer, enqueueAudio, clearAudioBuffer } from '../services/audio/audio-player';
import { websocketService } from '../services/websocket-service';
import { arrayBufferToBase64, base64ToArrayBuffer } from '../utils/base64';

// Voice chat states
export const VOICE_CHAT_STATES = {
  IDLE: 'idle',
  REQUESTING_PERMISSIONS: 'requesting_permissions',
  CONNECTING_WS: 'connecting_ws',
  READY: 'ready',
  LISTENING: 'listening',
  SPEAKING: 'speaking',
  ERROR: 'error',
  PERMISSION_DENIED: 'permission_denied',
  CONNECTION_ERROR: 'connection_error',
  RECONNECTING: 'reconnecting',
};

export function useVoiceChat() {
  const [state, setState] = useState(VOICE_CHAT_STATES.IDLE);
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);

  // Buffer for audio chunks (200ms intervals)
  const audioBufferRef = useRef([]);
  const bufferTimerRef = useRef(null);
  const currentMessageIdRef = useRef(null);

  /**
   * Handle incoming audio data from recorder
   */
  const handleAudioData = useCallback((pcmBuffer) => {
    logger.audio(`Audio data received: ${pcmBuffer.byteLength} bytes`);

    // Add to buffer
    audioBufferRef.current.push(pcmBuffer);

    // Start buffer timer if not running
    if (!bufferTimerRef.current) {
      bufferTimerRef.current = setInterval(() => {
        if (audioBufferRef.current.length === 0) return;

        logger.audio(`Sending buffered audio: ${audioBufferRef.current.length} chunks`);

        // Calculate total length
        let totalLength = 0;
        for (const chunk of audioBufferRef.current) {
          totalLength += chunk.byteLength;
        }

        // Combine all chunks
        const combined = new Uint8Array(totalLength);
        let offset = 0;
        for (const chunk of audioBufferRef.current) {
          combined.set(new Uint8Array(chunk), offset);
          offset += chunk.byteLength;
        }

        // Convert to base64 and send
        const base64Audio = arrayBufferToBase64(combined.buffer);
        websocketService.sendAudio(base64Audio);

        // Clear buffer
        audioBufferRef.current = [];
        logger.audio('Audio buffer cleared');

      }, 200); // 200ms intervals
    }
  }, []);

  /**
   * Handle incoming WebSocket messages
   */
  const handleWebSocketMessage = useCallback((message) => {
    // Handle turn complete
    if (message.turn_complete) {
      logger.ui('Turn complete signal received');
      currentMessageIdRef.current = null;
      if (state === VOICE_CHAT_STATES.SPEAKING) {
        setState(VOICE_CHAT_STATES.READY);
      }
      return;
    }

    // Handle interrupt
    if (message.interrupted) {
      logger.ui('Interrupt signal received');
      clearAudioBuffer();
      currentMessageIdRef.current = null;
      setState(VOICE_CHAT_STATES.READY);
      return;
    }

    // Handle audio data
    if (message.mime_type === 'audio/pcm' && message.data) {
      logger.audio('Received audio from server');
      const audioBuffer = base64ToArrayBuffer(message.data);
      enqueueAudio(audioBuffer);

      if (state !== VOICE_CHAT_STATES.SPEAKING) {
        setState(VOICE_CHAT_STATES.SPEAKING);
      }
    }

    // Handle text data
    if (message.mime_type === 'text/plain' && message.data) {
      logger.ui('Received text from server:', message.data);

      // Create new message if needed
      if (!currentMessageIdRef.current) {
        currentMessageIdRef.current = Math.random().toString(36).substring(7);
        setTranscript(prev => [
          ...prev,
          { id: currentMessageIdRef.current, role: 'agent', text: message.data }
        ]);
      } else {
        // Append to existing message (streaming)
        setTranscript(prev =>
          prev.map(msg =>
            msg.id === currentMessageIdRef.current
              ? { ...msg, text: msg.text + message.data }
              : msg
          )
        );
      }
    }
  }, [state]);

  /**
   * Start voice chat session
   */
  const startSession = useCallback(async () => {
    logger.ui('🚀 Starting voice chat session...');
    logger.ui(`State transition: ${state} → ${VOICE_CHAT_STATES.REQUESTING_PERMISSIONS}`);

    setState(VOICE_CHAT_STATES.REQUESTING_PERMISSIONS);
    setError(null);

    try {
      // Step 1: Initialize audio recorder
      const recorderResult = await initAudioRecorder(handleAudioData);
      if (!recorderResult.success) {
        throw new Error(`Recorder init failed: ${recorderResult.error}`);
      }

      // Step 2: Initialize audio player
      const playerResult = await initAudioPlayer();
      if (!playerResult.success) {
        throw new Error(`Player init failed: ${playerResult.error}`);
      }

      logger.ui(`State transition: ${VOICE_CHAT_STATES.REQUESTING_PERMISSIONS} → ${VOICE_CHAT_STATES.CONNECTING_WS}`);
      setState(VOICE_CHAT_STATES.CONNECTING_WS);

      // Step 3: Connect WebSocket
      websocketService.connect({
        isAudio: true,
        onOpen: () => {
          logger.ui(`State transition: ${VOICE_CHAT_STATES.CONNECTING_WS} → ${VOICE_CHAT_STATES.READY}`);
          setState(VOICE_CHAT_STATES.READY);
        },
        onMessage: handleWebSocketMessage,
        onClose: (event) => {
          if (!event.wasClean) {
            logger.ui(`State transition: ${state} → ${VOICE_CHAT_STATES.RECONNECTING}`);
            setState(VOICE_CHAT_STATES.RECONNECTING);
          }
        },
        onError: (error) => {
          logger.error('WebSocket error occurred');
          setError('Connection error. Retrying...');
          setState(VOICE_CHAT_STATES.CONNECTION_ERROR);
        }
      });

    } catch (err) {
      logger.error('❌ Failed to start session', err);

      if (err.message.includes('Permission denied') || err.name === 'NotAllowedError') {
        setError('Microphone permission denied. Please allow access and try again.');
        setState(VOICE_CHAT_STATES.PERMISSION_DENIED);
      } else {
        setError(err.message);
        setState(VOICE_CHAT_STATES.ERROR);
      }
    }
  }, [handleAudioData, handleWebSocketMessage, state]);

  /**
   * Stop voice chat session
   */
  const stopSession = useCallback(() => {
    logger.ui('🛑 Stopping voice chat session...');
    logger.ui(`State transition: ${state} → ${VOICE_CHAT_STATES.IDLE}`);

    // Clear buffer timer
    if (bufferTimerRef.current) {
      clearInterval(bufferTimerRef.current);
      bufferTimerRef.current = null;
    }

    // Stop audio services
    stopAudioRecorder();
    stopAudioPlayer();

    // Close WebSocket
    websocketService.close(false);

    // Reset state
    setState(VOICE_CHAT_STATES.IDLE);
    audioBufferRef.current = [];
    currentMessageIdRef.current = null;

    logger.ui('✅ Session stopped');
  }, [state]);

  /**
   * Send text message (for testing)
   */
  const sendText = useCallback((text) => {
    if (state !== VOICE_CHAT_STATES.READY && state !== VOICE_CHAT_STATES.LISTENING) {
      logger.ui('Cannot send text: Not in ready state');
      return;
    }

    logger.ui('Sending text message:', text);

    // Add to transcript
    setTranscript(prev => [
      ...prev,
      { id: Math.random().toString(36).substring(7), role: 'user', text }
    ]);

    // Send via WebSocket
    websocketService.sendText(text);
  }, [state]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      logger.ui('Component unmounting, cleaning up...');
      if (bufferTimerRef.current) {
        clearInterval(bufferTimerRef.current);
      }
      stopAudioRecorder();
      stopAudioPlayer();
      websocketService.close(false);
    };
  }, []);

  return {
    state,
    transcript,
    error,
    startSession,
    stopSession,
    sendText,
    isActive: state !== VOICE_CHAT_STATES.IDLE,
    isConnected: state === VOICE_CHAT_STATES.READY ||
                 state === VOICE_CHAT_STATES.LISTENING ||
                 state === VOICE_CHAT_STATES.SPEAKING,
  };
}
