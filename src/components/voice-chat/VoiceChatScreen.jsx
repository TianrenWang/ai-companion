/**
 * VoiceChatScreen Component
 * Main UI for voice chat interaction (MVP version)
 */

import { useEffect } from 'react';
import { useVoiceChat, VOICE_CHAT_STATES } from '../../hooks/useVoiceChat';
import { logger } from '../../config/audio-config';
import './VoiceChatScreen.css';

function VoiceChatScreen() {
  const {
    state,
    transcript,
    error,
    startSession,
    stopSession,
    sendText,
    isActive,
    isConnected
  } = useVoiceChat();

  useEffect(() => {
    logger.ui('VoiceChatScreen mounted');
    logger.ui('Initial state:', state);

    return () => {
      logger.ui('VoiceChatScreen unmounting');
    };
  }, [state]);

  /**
   * Handle start button click
   */
  const handleStartClick = () => {
    logger.ui('User clicked start button');
    startSession();
  };

  /**
   * Handle stop button click
   */
  const handleStopClick = () => {
    logger.ui('User clicked stop button');
    stopSession();
  };

  /**
   * Get button text based on state
   */
  const getButtonText = () => {
    switch (state) {
      case VOICE_CHAT_STATES.IDLE:
        return 'Let\'s Talk';
      case VOICE_CHAT_STATES.REQUESTING_PERMISSIONS:
        return 'Requesting Permissions...';
      case VOICE_CHAT_STATES.CONNECTING_WS:
        return 'Connecting...';
      case VOICE_CHAT_STATES.READY:
      case VOICE_CHAT_STATES.LISTENING:
      case VOICE_CHAT_STATES.SPEAKING:
        return 'Stop Talking';
      case VOICE_CHAT_STATES.RECONNECTING:
        return 'Reconnecting...';
      case VOICE_CHAT_STATES.PERMISSION_DENIED:
      case VOICE_CHAT_STATES.ERROR:
      case VOICE_CHAT_STATES.CONNECTION_ERROR:
        return 'Try Again';
      default:
        return 'Let\'s Talk';
    }
  };

  /**
   * Get status indicator color
   */
  const getStatusColor = () => {
    if (state === VOICE_CHAT_STATES.READY) return 'green';
    if (state === VOICE_CHAT_STATES.LISTENING) return 'blue';
    if (state === VOICE_CHAT_STATES.SPEAKING) return 'purple';
    if (state === VOICE_CHAT_STATES.CONNECTING_WS || state === VOICE_CHAT_STATES.RECONNECTING) return 'yellow';
    if (state === VOICE_CHAT_STATES.ERROR || state === VOICE_CHAT_STATES.PERMISSION_DENIED) return 'red';
    return 'gray';
  };

  /**
   * Check if button should be disabled
   */
  const isButtonDisabled = () => {
    return state === VOICE_CHAT_STATES.REQUESTING_PERMISSIONS ||
           state === VOICE_CHAT_STATES.CONNECTING_WS ||
           state === VOICE_CHAT_STATES.RECONNECTING;
  };

  return (
    <div className="voice-chat-screen">
      {/* Header */}
      <header className="voice-chat-header">
        <div className="logo">NORA</div>
        <div className="status-indicator">
          <div className={`status-dot ${getStatusColor()}`}></div>
          <span className="status-text">{state}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="voice-chat-content">
        {/* Avatar Area */}
        <div className="avatar-area">
          <div className="avatar-placeholder">
            {/* Simple avatar for MVP - can be replaced with Figma design */}
            <div className="avatar-circle">
              <div className={`avatar-pulse ${isConnected ? 'active' : ''}`}></div>
            </div>
          </div>
        </div>

        {/* Greeting / Transcript Area */}
        <div className="transcript-area">
          {transcript.length === 0 && state === VOICE_CHAT_STATES.IDLE && (
            <div className="greeting">
              <h1>Hi Mary,</h1>
              <h2>I'm looking forward to our conversation today!</h2>
            </div>
          )}

          {transcript.length > 0 && (
            <div className="transcript-messages">
              {transcript.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.role}`}
                >
                  <span className="message-label">
                    {message.role === 'user' ? 'You:' : 'Nora:'}
                  </span>
                  <span className="message-text">{message.text}</span>
                </div>
              ))}
            </div>
          )}

          {error && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Connection Status Messages */}
          {state === VOICE_CHAT_STATES.CONNECTING_WS && (
            <div className="status-message">Establishing connection...</div>
          )}
          {state === VOICE_CHAT_STATES.RECONNECTING && (
            <div className="status-message">Reconnecting...</div>
          )}
        </div>

        {/* Button Area */}
        <div className="button-area">
          <button
            className={`voice-button ${isActive ? 'active' : ''}`}
            onClick={isActive ? handleStopClick : handleStartClick}
            disabled={isButtonDisabled()}
          >
            {getButtonText()}
          </button>
        </div>

        {/* Debug Info (MVP only) */}
        <div className="debug-info">
          <div className="debug-row">
            <strong>State:</strong> {state}
          </div>
          <div className="debug-row">
            <strong>Connected:</strong> {isConnected ? 'Yes' : 'No'}
          </div>
          <div className="debug-row">
            <strong>Messages:</strong> {transcript.length}
          </div>
          <div className="debug-hint">
            💡 Open browser console (F12) to see detailed logs
          </div>
        </div>
      </main>
    </div>
  );
}

export default VoiceChatScreen;
