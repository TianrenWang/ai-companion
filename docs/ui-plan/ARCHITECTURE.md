# Voice Chat UI Architecture

## Overview
Building a React-based voice chat application based on Google's ADK Streaming WebSocket tutorial. The app enables real-time bidirectional audio/text communication with an AI companion.

## Current Status: MVP Phase

### Goals
- Create a lightweight React implementation of the static HTML demo
- Add extensive console logging for debugging
- Test audio pipeline with real credentials
- Validate WebSocket connection and streaming

---

## Architecture Layers

### 1. **Configuration Layer** (`/src/config/`)
- `audio-config.js` - Centralized audio settings and logger utilities

**Key Settings:**
- Recorder: 16kHz sample rate
- Player: 24kHz sample rate
- Buffer interval: 200ms chunks
- Debug logging: Enabled

### 2. **Utility Layer** (`/src/utils/`)
- `base64.js` - Audio encoding/decoding utilities
  - ArrayBuffer ↔ Base64 conversion
  - Float32 ↔ PCM16 conversion

### 3. **Service Layer** (`/src/services/`)

#### Audio Services (`/services/audio/`)
- `audio-recorder.js` - Microphone capture + PCM encoding
- `audio-player.js` - Audio playback + buffer management
- Uses Web Audio API AudioWorklets (from `/static/js/`)

#### WebSocket Service
- `websocket-service.js` - Connection management, message routing, auto-reconnect

**Message Format:**
```javascript
// Client → Server
{
  mime_type: "audio/pcm" | "text/plain",
  data: "<base64_or_text>"
}

// Server → Client
{
  mime_type: "audio/pcm" | "text/plain",
  data: "<base64_or_text>",
  turn_complete: boolean,
  interrupted: boolean
}
```

### 4. **Hook Layer** (`/src/hooks/`)
React custom hooks for state management:
- `useWebSocket.js` - WebSocket connection lifecycle
- `useAudioRecorder.js` - Mic recording with buffering
- `useAudioPlayer.js` - Audio playback stream
- `useVoiceChat.js` - Main orchestrator (combines above)

### 5. **Component Layer** (`/src/components/`)

#### Voice Chat Components
- `VoiceChatScreen.jsx` - Main UI container
- `Avatar.jsx` - Animated character (Figma design)
- `TranscriptDisplay.jsx` - Streaming conversation text
- `VoiceButton.jsx` - Start/Stop CTA
- `ConnectionStatus.jsx` - WebSocket status indicator

---

## State Machine

```
IDLE → (user clicks button)
  ↓
REQUESTING_PERMISSIONS → (mic granted)
  ↓
CONNECTING_WS → (WebSocket opens)
  ↓
READY → (user speaks)
  ↓
LISTENING → (silence detected or turn_complete)
  ↓
PROCESSING → (server responds)
  ↓
SPEAKING → (audio ends or interrupted)
  ↓
READY (loop back)
```

**Error States:**
- `PERMISSION_DENIED` - Mic access rejected
- `CONNECTION_ERROR` - WebSocket failed
- `RECONNECTING` - Auto-reconnect in progress

---

## Audio Pipeline

### Recording Flow
```
Microphone
  ↓ (MediaStream)
AudioContext (16kHz)
  ↓
MediaStreamSource
  ↓
AudioWorkletNode (pcm-recorder-processor.js)
  ↓ (Float32Array via MessagePort)
Main Thread
  ↓ (convert to Int16)
Buffer Manager (200ms chunks)
  ↓ (Base64 encode)
WebSocket
```

### Playback Flow
```
WebSocket
  ↓ (Base64 string)
Base64 Decoder
  ↓ (ArrayBuffer)
AudioWorkletNode (pcm-player-processor.js)
  ↓ (Ring buffer, Float32 conversion)
AudioContext.destination (24kHz)
  ↓
Speakers
```

---

## Console Logging Strategy

### Log Prefixes
- `[AUDIO]` - Audio capture/playback events
- `[WEBSOCKET]` - Connection state, messages
- `[UI]` - Component lifecycle, user interactions
- `[ERROR]` - All errors with stack traces

### Key Checkpoints
1. **Initialization**
   - ✓ Mic permission granted
   - ✓ AudioContext created (sample rate)
   - ✓ Worklet loaded
   - ✓ WebSocket connected

2. **Audio Flow**
   - Audio chunk received (sample count)
   - PCM conversion (bytes)
   - Base64 encoding (length)
   - WebSocket send (payload size)

3. **Playback**
   - Server message received (type)
   - Base64 decode (buffer size)
   - Worklet enqueue (samples added)
   - Buffer health (fill level)

4. **State Transitions**
   - State change: IDLE → CONNECTING
   - Turn complete received
   - Interrupt signal handled

---

## File Structure (MVP)

```
src/
├── config/
│   └── audio-config.js ✅
├── utils/
│   └── base64.js ✅
├── services/
│   ├── audio/
│   │   ├── audio-recorder.js ✅
│   │   └── audio-player.js ⏳
│   └── websocket-service.js ⏳
├── hooks/
│   ├── useWebSocket.js ⏳
│   ├── useAudioRecorder.js ⏳
│   ├── useAudioPlayer.js ⏳
│   └── useVoiceChat.js ⏳
└── components/
    └── voice-chat/
        └── VoiceChatScreen.jsx ⏳

static/js/ (unchanged, used by services)
├── pcm-player-processor.js
└── pcm-recorder-processor.js

docs/ui-plan/ (documentation)
├── ARCHITECTURE.md (this file)
└── MVP-TESTING.md
```

---

## WebSocket URL Format

```javascript
const sessionId = crypto.randomUUID(); // or Math.random()
const wsUrl = `ws://${window.location.host}/ws/${sessionId}?is_audio=true`;
```

**Query Parameters:**
- `is_audio=true` - Enable audio mode (vs text-only)

---

## Dependencies

**Required:**
- React 18.2+
- Vite (build tool)

**No Additional Packages Needed:**
- Uses native Web Audio API
- Uses native WebSocket API
- Uses native Base64 encoding

---

## Testing Strategy

### Phase 1: Component Testing
- Audio permission flow
- WebSocket connection handshake
- Audio capture (check console for chunks)
- Audio playback (verify ring buffer)

### Phase 2: Integration Testing
- End-to-end voice conversation
- Interrupt handling
- Reconnection after disconnect
- Error recovery

### Phase 3: Performance Testing
- Latency measurement
- Buffer overflow handling
- Memory leak detection
- Mobile browser compatibility

---

## Known Constraints

1. **Browser Compatibility**
   - Chrome 66+ (AudioWorklet support)
   - Safari 14.1+ (requires user gesture for AudioContext)
   - Firefox 76+

2. **Security Requirements**
   - HTTPS required (or localhost)
   - User gesture needed to start audio
   - Microphone permissions prompt

3. **Performance**
   - 200ms buffering = ~3.2KB per chunk @ 16kHz
   - Ring buffer holds 3 minutes of audio
   - Base64 overhead: 33% size increase

---

## Next Steps

1. ✅ Complete audio-player.js
2. ✅ Build websocket-service.js
3. ✅ Create React hooks
4. ✅ Build VoiceChatScreen component
5. ✅ Integration testing with server
6. ✅ Debug console logging validation
