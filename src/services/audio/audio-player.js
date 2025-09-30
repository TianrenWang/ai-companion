/**
 * Audio Player Service
 * Handles audio playback using Web Audio API and ring buffer
 */

import { AUDIO_CONFIG, logger } from '../../config/audio-config';

let audioContext = null;
let audioWorkletNode = null;

/**
 * Initialize audio player for playback
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function initAudioPlayer() {
  logger.audio('🔊 Initializing audio player...');

  try {
    // Step 1: Create AudioContext with playback sample rate
    logger.audio(`Creating AudioContext (${AUDIO_CONFIG.PLAYER_SAMPLE_RATE}Hz)...`);
    audioContext = new AudioContext({
      sampleRate: AUDIO_CONFIG.PLAYER_SAMPLE_RATE
    });
    logger.audio('✓ AudioContext created', {
      sampleRate: audioContext.sampleRate,
      state: audioContext.state,
    });

    // Step 2: Load audio worklet processor
    logger.audio('Loading audio worklet processor...');
    const workletPath = new URL(
      '../../../static/js/pcm-player-processor.js',
      import.meta.url
    );
    await audioContext.audioWorklet.addModule(workletPath);
    logger.audio('✓ Worklet processor loaded');

    // Step 3: Create audio worklet node
    logger.audio('Creating AudioWorkletNode...');
    audioWorkletNode = new AudioWorkletNode(
      audioContext,
      'pcm-player-processor'
    );

    // Step 4: Connect worklet to speakers
    logger.audio('Connecting audio pipeline...');
    audioWorkletNode.connect(audioContext.destination);
    logger.audio('✓ Audio pipeline connected: Worklet → Speakers');

    logger.audio('✅ Audio player initialized successfully');
    return { success: true };

  } catch (error) {
    logger.error('❌ Failed to initialize audio player', error);
    return {
      success: false,
      error: error.message || 'Unknown error'
    };
  }
}

/**
 * Enqueue audio data to the player buffer
 * @param {ArrayBuffer} audioData - Int16 PCM audio data
 */
export function enqueueAudio(audioData) {
  if (!audioWorkletNode) {
    logger.error('Cannot enqueue audio: Player not initialized');
    return;
  }

  const int16Array = new Int16Array(audioData);
  logger.audio(`Enqueueing audio to player: ${int16Array.length} samples`);

  audioWorkletNode.port.postMessage(audioData);
  logger.audio('✓ Audio data sent to worklet');
}

/**
 * Clear the audio buffer (used for interrupts)
 */
export function clearAudioBuffer() {
  if (!audioWorkletNode) {
    logger.error('Cannot clear buffer: Player not initialized');
    return;
  }

  logger.audio('Clearing audio player buffer...');
  audioWorkletNode.port.postMessage({ command: 'endOfAudio' });
  logger.audio('✓ Player buffer cleared');
}

/**
 * Stop audio player and cleanup resources
 */
export function stopAudioPlayer() {
  logger.audio('🛑 Stopping audio player...');

  try {
    // Disconnect worklet
    if (audioWorkletNode) {
      audioWorkletNode.disconnect();
      logger.audio('✓ Player worklet disconnected');
    }

    // Close audio context
    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close();
      logger.audio('✓ Player AudioContext closed');
    }

    // Reset references
    audioContext = null;
    audioWorkletNode = null;

    logger.audio('✅ Audio player stopped');

  } catch (error) {
    logger.error('❌ Error stopping audio player', error);
  }
}

/**
 * Check if audio player is currently active
 * @returns {boolean}
 */
export function isPlayerActive() {
  const active = audioContext !== null && audioContext.state === 'running';
  logger.audio('Player active check:', active);
  return active;
}

/**
 * Resume audio context (required after user gesture on some browsers)
 */
export async function resumeAudioContext() {
  if (audioContext && audioContext.state === 'suspended') {
    logger.audio('Resuming suspended AudioContext...');
    await audioContext.resume();
    logger.audio('✓ AudioContext resumed');
  }
}
