/**
 * WebSocket Service
 * Manages WebSocket connection for bidirectional streaming
 */

import { AUDIO_CONFIG, logger } from '../config/audio-config';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.sessionId = null;
    this.reconnectAttempts = 0;
    this.reconnectTimer = null;
    this.shouldReconnect = true;

    // Callbacks
    this.onOpenCallback = null;
    this.onMessageCallback = null;
    this.onCloseCallback = null;
    this.onErrorCallback = null;
  }

  /**
   * Generate a unique session ID
   */
  generateSessionId() {
    // Use crypto.randomUUID if available, fallback to Math.random
    if (crypto.randomUUID) {
      return crypto.randomUUID();
    }
    return Math.random().toString(36).substring(2, 15) +
           Math.random().toString(36).substring(2, 15);
  }

  /**
   * Connect to WebSocket server
   * @param {Object} options - Connection options
   * @param {boolean} options.isAudio - Enable audio mode
   * @param {Function} options.onOpen - Called when connection opens
   * @param {Function} options.onMessage - Called when message received
   * @param {Function} options.onClose - Called when connection closes
   * @param {Function} options.onError - Called on error
   */
  connect(options = {}) {
    const {
      isAudio = true,
      onOpen,
      onMessage,
      onClose,
      onError
    } = options;

    // Store callbacks
    this.onOpenCallback = onOpen;
    this.onMessageCallback = onMessage;
    this.onCloseCallback = onClose;
    this.onErrorCallback = onError;

    // Generate session ID if not exists
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      logger.ws('Generated session ID:', this.sessionId);
    }

    // Build WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.host || 'localhost:8000';
    const wsUrl = `${wsProtocol}//${wsHost}/ws/${this.sessionId}?is_audio=${isAudio}`;

    logger.ws('🔌 Connecting to WebSocket...', wsUrl);

    try {
      // Create WebSocket connection
      this.ws = new WebSocket(wsUrl);

      // Set up event handlers
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);

    } catch (error) {
      logger.error('❌ Failed to create WebSocket connection', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
    }
  }

  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    logger.ws('✓ Connection opened');
    logger.ws('Connection state:', this.getReadyState());

    this.reconnectAttempts = 0;

    if (this.onOpenCallback) {
      this.onOpenCallback(event);
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      logger.ws('← [AGENT TO CLIENT]', {
        mime_type: message.mime_type,
        data_length: message.data ? message.data.length : 0,
        turn_complete: message.turn_complete,
        interrupted: message.interrupted
      });

      if (this.onMessageCallback) {
        this.onMessageCallback(message);
      }

    } catch (error) {
      logger.error('❌ Failed to parse WebSocket message', error);
      logger.error('Raw message:', event.data);
    }
  }

  /**
   * Handle WebSocket close event
   */
  handleClose(event) {
    logger.ws('🔌 Connection closed', {
      code: event.code,
      reason: event.reason || 'No reason provided',
      wasClean: event.wasClean
    });

    if (this.onCloseCallback) {
      this.onCloseCallback(event);
    }

    // Auto-reconnect if not a clean close and reconnect is enabled
    if (this.shouldReconnect && !event.wasClean) {
      this.scheduleReconnect();
    }
  }

  /**
   * Handle WebSocket error event
   */
  handleError(event) {
    logger.error('❌ WebSocket error', event);

    if (this.onErrorCallback) {
      this.onErrorCallback(event);
    }
  }

  /**
   * Schedule automatic reconnection
   */
  scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = AUDIO_CONFIG.WS_RECONNECT_DELAY_MS;

    logger.ws(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);

    this.reconnectTimer = setTimeout(() => {
      logger.ws('Attempting to reconnect...');
      this.connect({
        isAudio: true,
        onOpen: this.onOpenCallback,
        onMessage: this.onMessageCallback,
        onClose: this.onCloseCallback,
        onError: this.onErrorCallback
      });
    }, delay);
  }

  /**
   * Send a message through WebSocket
   * @param {Object} message - Message object with mime_type and data
   */
  send(message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      logger.error('Cannot send message: WebSocket not open', this.getReadyState());
      return false;
    }

    try {
      const messageJson = JSON.stringify(message);

      logger.ws('→ [CLIENT TO AGENT]', {
        mime_type: message.mime_type,
        data_length: message.data ? message.data.length : 0
      });

      this.ws.send(messageJson);
      return true;

    } catch (error) {
      logger.error('❌ Failed to send message', error);
      return false;
    }
  }

  /**
   * Send text message
   * @param {string} text - Text to send
   */
  sendText(text) {
    logger.ws('Sending text message:', text);
    return this.send({
      mime_type: 'text/plain',
      data: text
    });
  }

  /**
   * Send audio message
   * @param {string} base64Audio - Base64 encoded audio data
   */
  sendAudio(base64Audio) {
    logger.ws('Sending audio data:', `${base64Audio.length} chars (base64)`);
    return this.send({
      mime_type: 'audio/pcm',
      data: base64Audio
    });
  }

  /**
   * Close WebSocket connection
   * @param {boolean} shouldReconnect - Whether to allow auto-reconnect
   */
  close(shouldReconnect = false) {
    this.shouldReconnect = shouldReconnect;

    // Clear reconnect timer
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      logger.ws('Closing WebSocket connection...');
      this.ws.close(1000, 'Client closed connection');
      this.ws = null;
    }
  }

  /**
   * Get current WebSocket ready state as string
   * @returns {string}
   */
  getReadyState() {
    if (!this.ws) return 'NOT_CONNECTED';

    const states = {
      [WebSocket.CONNECTING]: 'CONNECTING',
      [WebSocket.OPEN]: 'OPEN',
      [WebSocket.CLOSING]: 'CLOSING',
      [WebSocket.CLOSED]: 'CLOSED'
    };

    return states[this.ws.readyState] || 'UNKNOWN';
  }

  /**
   * Check if WebSocket is currently connected
   * @returns {boolean}
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;
