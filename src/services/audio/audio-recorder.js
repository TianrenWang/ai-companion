/**
 * Audio Recorder Service
 * Handles microphone capture and PCM encoding using Web Audio API
 */

import { AUDIO_CONFIG, logger } from '../../config/audio-config';
import { float32ToPCM16 } from '../../utils/base64';

let audioContext = null;
let audioWorkletNode = null;
let mediaStream = null;
let sourceNode = null;

/**
 * Initialize audio recorder with microphone access
 * @param {Function} onAudioData - Callback receiving PCM data as ArrayBuffer
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function initAudioRecorder(onAudioData) {
  logger.audio('🎤 Initializing audio recorder...');

  try {
    // Step 1: Request microphone permissions
    logger.audio('Requesting microphone permissions...');
    mediaStream = await navigator.mediaDevices.getUserMedia(
      AUDIO_CONFIG.MIC_CONSTRAINTS
    );
    logger.audio('✓ Microphone access granted', mediaStream.getTracks()[0].label);

    // Step 2: Create AudioContext with specific sample rate
    logger.audio(`Creating AudioContext (${AUDIO_CONFIG.RECORDER_SAMPLE_RATE}Hz)...`);
    audioContext = new AudioContext({
      sampleRate: AUDIO_CONFIG.RECORDER_SAMPLE_RATE
    });
    logger.audio('✓ AudioContext created', {
      sampleRate: audioContext.sampleRate,
      state: audioContext.state,
    });

    // Step 3: Load audio worklet processor
    logger.audio('Loading audio worklet processor...');
    const workletPath = new URL(
      '../../../static/js/pcm-recorder-processor.js',
      import.meta.url
    );
    await audioContext.audioWorklet.addModule(workletPath);
    logger.audio('✓ Worklet processor loaded');

    // Step 4: Create audio worklet node
    logger.audio('Creating AudioWorkletNode...');
    audioWorkletNode = new AudioWorkletNode(
      audioContext,
      'pcm-recorder-processor'
    );

    // Step 5: Connect microphone to worklet
    logger.audio('Connecting audio pipeline...');
    sourceNode = audioContext.createMediaStreamSource(mediaStream);
    sourceNode.connect(audioWorkletNode);
    logger.audio('✓ Audio pipeline connected: Mic → Worklet');

    // Step 6: Set up message handler for audio data
    audioWorkletNode.port.onmessage = (event) => {
      const float32Data = event.data;
      logger.audio(`Received audio chunk: ${float32Data.length} samples`);

      // Convert Float32 to 16-bit PCM
      const pcmBuffer = float32ToPCM16(float32Data);

      // Send to callback
      onAudioData(pcmBuffer);
    };

    logger.audio('✅ Audio recorder initialized successfully');
    return { success: true };

  } catch (error) {
    logger.error('❌ Failed to initialize audio recorder', error);
    return {
      success: false,
      error: error.message || 'Unknown error'
    };
  }
}

/**
 * Stop audio recording and cleanup resources
 */
export function stopAudioRecorder() {
  logger.audio('🛑 Stopping audio recorder...');

  try {
    // Disconnect nodes
    if (sourceNode) {
      sourceNode.disconnect();
      logger.audio('✓ Source node disconnected');
    }

    if (audioWorkletNode) {
      audioWorkletNode.disconnect();
      logger.audio('✓ Worklet node disconnected');
    }

    // Stop media tracks
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => {
        track.stop();
        logger.audio('✓ Media track stopped', track.label);
      });
    }

    // Close audio context
    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close();
      logger.audio('✓ AudioContext closed');
    }

    // Reset references
    audioContext = null;
    audioWorkletNode = null;
    mediaStream = null;
    sourceNode = null;

    logger.audio('✅ Audio recorder stopped and cleaned up');

  } catch (error) {
    logger.error('❌ Error stopping audio recorder', error);
  }
}

/**
 * Check if audio recorder is currently active
 * @returns {boolean}
 */
export function isRecorderActive() {
  const active = audioContext !== null && audioContext.state === 'running';
  logger.audio('Recorder active check:', active);
  return active;
}
