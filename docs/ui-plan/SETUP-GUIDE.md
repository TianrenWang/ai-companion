# MVP Setup & Testing Guide

## Quick Start

### 1. Install Dependencies (if needed)
```bash
cd /Users/seyitanoke/Documents/Nora/ai-companion
npm install
```

### 2. Start Development Server
```bash
npm run dev
# or
vite
```

### 3. Open Browser
Navigate to: `http://localhost:5173` (or the port shown in terminal)

### 4. Open Browser Console
Press `F12` or `Cmd+Option+I` (Mac) to open DevTools and view console logs

---

## Testing the Audio Pipeline

### Step 1: Initial Load
**Expected Console Output:**
```
[UI] VoiceChatScreen mounted
[UI] Initial state: idle
```

**Visual Check:**
- Page loads with greeting "Hi Mary, I'm looking forward..."
- "Let's Talk" button is visible
- Status shows "idle" with gray dot
- Debug info shows at bottom

---

### Step 2: Click "Let's Talk" Button

**Expected Console Output:**
```
[UI] User clicked start button
[UI] 🚀 Starting voice chat session...
[UI] State transition: idle → requesting_permissions
[AUDIO] 🎤 Initializing audio recorder...
[AUDIO] Requesting microphone permissions...
```

**Browser Popup:**
- Browser will ask for microphone permission
- Click "Allow"

**After Permission Granted:**
```
[AUDIO] ✓ Microphone access granted <device name>
[AUDIO] Creating AudioContext (16000Hz)...
[AUDIO] ✓ AudioContext created { sampleRate: 16000, state: "running" }
[AUDIO] Loading audio worklet processor...
[AUDIO] ✓ Worklet processor loaded
[AUDIO] Creating AudioWorkletNode...
[AUDIO] Connecting audio pipeline...
[AUDIO] ✓ Audio pipeline connected: Mic → Worklet
[AUDIO] ✅ Audio recorder initialized successfully

[AUDIO] 🔊 Initializing audio player...
[AUDIO] Creating AudioContext (24000Hz)...
[AUDIO] ✓ AudioContext created { sampleRate: 24000, state: "running" }
[AUDIO] Loading audio worklet processor...
[AUDIO] ✓ Worklet processor loaded
[AUDIO] Creating AudioWorkletNode...
[AUDIO] Connecting audio pipeline...
[AUDIO] ✓ Audio pipeline connected: Worklet → Speakers
[AUDIO] ✅ Audio player initialized successfully

[UI] State transition: requesting_permissions → connecting_ws
[WEBSOCKET] 🔌 Connecting to WebSocket... ws://localhost:8000/ws/<uuid>?is_audio=true
[WEBSOCKET] Generated session ID: <uuid>
```

**Visual Check:**
- Button text changes to "Connecting..."
- Status shows "connecting_ws" with yellow dot
- Avatar pulse animation should start

---

### Step 3: WebSocket Connection

**Expected Console Output (Success):**
```
[WEBSOCKET] ✓ Connection opened
[WEBSOCKET] Connection state: OPEN
[UI] State transition: connecting_ws → ready
```

**Expected Console Output (Failure):**
```
[WEBSOCKET] ❌ Connection error Event { ... }
[WEBSOCKET] Will retry in 5000ms
[UI] State transition: connecting_ws → connection_error
```

**Visual Check (Success):**
- Button text changes to "Stop Talking"
- Status shows "ready" with green dot
- Avatar pulse is active

---

### Step 4: Speaking (Audio Recording)

**While speaking into microphone, expected output every 200ms:**
```
[AUDIO] Received audio chunk: 3200 samples
[AUDIO] Converting Float32 to PCM16, samples: 3200
[AUDIO] PCM16 conversion complete, bytes: 6400
[AUDIO] Sending buffered audio: 1 chunks
[AUDIO] Converting ArrayBuffer to Base64, size: 6400 bytes
[AUDIO] Base64 conversion complete, output length: 8534
[WEBSOCKET] Sending audio data: 8534 chars (base64)
[WEBSOCKET] → [CLIENT TO AGENT] { mime_type: "audio/pcm", data_length: 8534 }
[AUDIO] Audio buffer cleared
```

**Visual Check:**
- Status should show "listening" when actively sending audio
- No lag or freezing

---

### Step 5: Receiving Response

**Expected Console Output (Text Response):**
```
[WEBSOCKET] ← [AGENT TO CLIENT] { mime_type: "text/plain", data_length: 25, ... }
[UI] Received text from server: Hello! How can I help you?
```

**Expected Console Output (Audio Response):**
```
[WEBSOCKET] ← [AGENT TO CLIENT] { mime_type: "audio/pcm", data_length: 12000, ... }
[AUDIO] Received audio from server
[AUDIO] Converting Base64 to ArrayBuffer, input length: 12000
[AUDIO] ArrayBuffer conversion complete, size: 9000 bytes
[AUDIO] Enqueueing audio to player: 5625 samples
[AUDIO] ✓ Audio data sent to worklet
```

**Visual Check:**
- Text appears in transcript area
- Audio plays through speakers
- Status changes to "speaking" with purple dot

**Expected Console Output (Turn Complete):**
```
[WEBSOCKET] ← [AGENT TO CLIENT] { turn_complete: true }
[UI] Turn complete signal received
[UI] State transition: speaking → ready
```

---

### Step 6: Stop Session

**Click "Stop Talking" button:**
```
[UI] User clicked stop button
[UI] 🛑 Stopping voice chat session...
[UI] State transition: ready → idle

[AUDIO] 🛑 Stopping audio recorder...
[AUDIO] ✓ Source node disconnected
[AUDIO] ✓ Worklet node disconnected
[AUDIO] ✓ Media track stopped <device name>
[AUDIO] ✓ AudioContext closed
[AUDIO] ✅ Audio recorder stopped and cleaned up

[AUDIO] 🛑 Stopping audio player...
[AUDIO] ✓ Player worklet disconnected
[AUDIO] ✓ Player AudioContext closed
[AUDIO] ✅ Audio player stopped

[WEBSOCKET] Closing WebSocket connection...
[WEBSOCKET] ✓ Connection closed gracefully
[UI] ✅ Session stopped
```

**Visual Check:**
- Button returns to "Let's Talk"
- Status returns to "idle" with gray dot
- Avatar pulse stops
- Transcript remains visible

---

## Troubleshooting

### Issue: "Cannot find module '../../../static/js/pcm-recorder-processor.js'"

**Solution:**
The worklet files must be in the `static/js/` directory. Verify they exist:
```bash
ls -la static/js/
```

Should show:
- `pcm-player-processor.js`
- `pcm-recorder-processor.js`

### Issue: Microphone permission denied

**Console Output:**
```
[ERROR] ❌ Failed to initialize audio recorder NotAllowedError: Permission denied
[UI] State transition: idle → permission_denied
```

**Solution:**
1. Check browser settings → Privacy → Microphone
2. Ensure localhost is allowed
3. Try in a different browser
4. On Mac: System Preferences → Security & Privacy → Microphone

### Issue: WebSocket connection fails

**Console Output:**
```
[WEBSOCKET] ❌ Connection error
[WEBSOCKET] 🔄 Auto-reconnect triggered
```

**Solution:**
1. Verify backend server is running
2. Check the WebSocket URL in console
3. Ensure port matches server (default: 8000)
4. Check firewall settings

### Issue: No audio chunks appearing

**Solution:**
1. Verify mic is not muted
2. Check browser microphone permissions
3. Look for AudioContext state in console
4. Try speaking louder

### Issue: Audio sounds distorted

**Solution:**
1. Check sample rate mismatch in console logs
2. Verify PCM16 conversion is working
3. Check for buffer overflow warnings
4. Reduce system audio volume

---

## Configuration

### Change WebSocket URL

Edit `src/services/websocket-service.js`:
```javascript
// Line ~47
const wsHost = window.location.host || 'localhost:8000';
// Change to your server address
```

### Change Audio Settings

Edit `src/config/audio-config.js`:
```javascript
RECORDER_SAMPLE_RATE: 16000,  // Recording sample rate
PLAYER_SAMPLE_RATE: 24000,    // Playback sample rate
BUFFER_INTERVAL_MS: 200,      // Audio chunk interval
DEBUG: true,                   // Enable/disable console logs
```

### Disable Debug Logs

In `src/config/audio-config.js`:
```javascript
DEBUG: false,  // Set to false to disable verbose logging
```

---

## Production Checklist

Before deploying to production:

1. ✅ Set `DEBUG: false` in audio-config.js
2. ✅ Remove debug info panel from VoiceChatScreen.jsx
3. ✅ Replace avatar placeholder with Figma design
4. ✅ Add proper error boundaries
5. ✅ Test on multiple browsers (Chrome, Safari, Firefox)
6. ✅ Test on mobile devices
7. ✅ Add analytics/monitoring
8. ✅ Implement proper reconnection UX
9. ✅ Add loading skeletons
10. ✅ Optimize bundle size

---

## Next Steps

After MVP is working:

1. **Enhance UI** - Implement full Figma design
2. **Add Animations** - Framer Motion for smooth transitions
3. **Improve UX** - Better error handling, loading states
4. **Add Features** - Conversation history, settings panel
5. **Performance** - Optimize audio buffering, reduce latency
6. **Accessibility** - Keyboard navigation, screen reader support
7. **Testing** - Unit tests, integration tests, E2E tests

---

## File Structure Reference

```
src/
├── config/
│   └── audio-config.js          ✅ Audio settings & logger
├── utils/
│   └── base64.js                ✅ Encoding/decoding utilities
├── services/
│   ├── audio/
│   │   ├── audio-recorder.js    ✅ Mic capture
│   │   └── audio-player.js      ✅ Audio playback
│   └── websocket-service.js     ✅ WebSocket client
├── hooks/
│   └── useVoiceChat.js          ✅ Main orchestrator hook
├── components/
│   └── voice-chat/
│       ├── VoiceChatScreen.jsx  ✅ Main UI component
│       └── VoiceChatScreen.css  ✅ Styles
└── App.jsx                      ✅ Updated with VoiceChatScreen

static/js/
├── pcm-player-processor.js      ✅ Audio worklet (playback)
└── pcm-recorder-processor.js    ✅ Audio worklet (recording)

docs/ui-plan/
├── ARCHITECTURE.md              ✅ Architecture overview
├── MVP-TESTING.md               ✅ Testing guide
└── SETUP-GUIDE.md               ✅ This file
```
