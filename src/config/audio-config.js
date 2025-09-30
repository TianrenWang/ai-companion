/**
 * Audio Configuration
 * Central configuration for audio settings
 */

export const AUDIO_CONFIG = {
  // Sample rates
  RECORDER_SAMPLE_RATE: 16000,  // 16kHz for recording (matches server)
  PLAYER_SAMPLE_RATE: 24000,    // 24kHz for playback (matches server)

  // Buffer settings
  BUFFER_INTERVAL_MS: 200,      // Send audio chunks every 200ms
  PLAYER_BUFFER_SECONDS: 180,   // 3 minutes of audio buffer

  // Audio constraints
  MIC_CONSTRAINTS: {
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    }
  },

  // WebSocket settings
  WS_RECONNECT_DELAY_MS: 5000,

  // Debug mode
  DEBUG: true,
};

// Console logger helper
export const logger = {
  audio: (message, ...args) => {
    if (AUDIO_CONFIG.DEBUG) {
      console.log(`[AUDIO] ${message}`, ...args);
    }
  },

  ws: (message, ...args) => {
    if (AUDIO_CONFIG.DEBUG) {
      console.log(`[WEBSOCKET] ${message}`, ...args);
    }
  },

  ui: (message, ...args) => {
    if (AUDIO_CONFIG.DEBUG) {
      console.log(`[UI] ${message}`, ...args);
    }
  },

  error: (message, ...args) => {
    console.error(`[ERROR] ${message}`, ...args);
  },
};
