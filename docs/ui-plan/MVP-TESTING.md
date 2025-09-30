# MVP Testing Guide

## Console Logging Checkpoints

This document outlines all console log messages you should see during normal operation. Use this to debug the audio pipeline.

---

## 1. Application Start

```
[UI] VoiceChatScreen mounted
[UI] Initial state: IDLE
```

---

## 2. User Clicks "Let's Talk" Button

### Step 1: Microphone Permission Request
```
[AUDIO] 🎤 Initializing audio recorder...
[AUDIO] Requesting microphone permissions...
```

**Success Path:**
```
[AUDIO] ✓ Microphone access granted <device_name>
[AUDIO] Creating AudioContext (16000Hz)...
[AUDIO] ✓ AudioContext created { sampleRate: 16000, state: "running" }
[AUDIO] Loading audio worklet processor...
[AUDIO] ✓ Worklet processor loaded
[AUDIO] Creating AudioWorkletNode...
[AUDIO] Connecting audio pipeline...
[AUDIO] ✓ Audio pipeline connected: Mic → Worklet
[AUDIO] ✅ Audio recorder initialized successfully
[UI] State transition: IDLE → CONNECTING_WS
```

**Failure Path (Permission Denied):**
```
[ERROR] ❌ Failed to initialize audio recorder NotAllowedError: Permission denied
[UI] State transition: IDLE → PERMISSION_DENIED
```

---

## 3. WebSocket Connection

### Step 1: Connection Attempt
```
[WEBSOCKET] 🔌 Connecting to ws://localhost:8000/ws/<session_id>?is_audio=true
[WEBSOCKET] Session ID: <uuid>
```

**Success Path:**
```
[WEBSOCKET] ✓ Connection opened
[WEBSOCKET] Connection state: OPEN
[UI] State transition: CONNECTING_WS → READY
```

**Failure Path:**
```
[WEBSOCKET] ❌ Connection error Event { ... }
[WEBSOCKET] Will retry in 5000ms
[UI] State transition: CONNECTING_WS → CONNECTION_ERROR
```

---

## 4. Audio Recording (Active Conversation)

### Every ~200ms while speaking:
```
[AUDIO] Received audio chunk: 3200 samples
[AUDIO] Converting Float32 to PCM16, samples: 3200
[AUDIO] PCM16 conversion complete, bytes: 6400
[AUDIO] Converting ArrayBuffer to Base64, size: 6400 bytes
[AUDIO] Base64 conversion complete, output length: 8534
[WEBSOCKET] Sending message { mime_type: "audio/pcm", data: "<base64>..." }
[WEBSOCKET] → [CLIENT TO AGENT] sent 6400 bytes
```

**Buffer Manager:**
```
[AUDIO] Buffer manager: 3 chunks accumulated
[AUDIO] Sending buffered audio: 19200 bytes total
[AUDIO] Buffer cleared
```

---

## 5. Server Response (AI Speaking)

### Text Response:
```
[WEBSOCKET] ← [AGENT TO CLIENT] { mime_type: "text/plain", data: "Hello! How can I..." }
[UI] Appending text to transcript: "Hello! How can I..."
```

### Audio Response:
```
[WEBSOCKET] ← [AGENT TO CLIENT] { mime_type: "audio/pcm", data: "<base64>..." }
[AUDIO] Converting Base64 to ArrayBuffer, input length: 12000
[AUDIO] ArrayBuffer conversion complete, size: 9000 bytes
[AUDIO] Enqueueing audio to player worklet
[AUDIO] Player buffer: 9000 samples added, fill level: 37%
[UI] State transition: READY → SPEAKING
```

### Turn Complete:
```
[WEBSOCKET] ← [AGENT TO CLIENT] { turn_complete: true }
[UI] Turn complete signal received
[UI] State transition: SPEAKING → READY
```

### Interrupt:
```
[WEBSOCKET] ← [AGENT TO CLIENT] { interrupted: true }
[AUDIO] Interrupt signal - clearing player buffer
[AUDIO] Player buffer reset
[UI] State transition: SPEAKING → READY
```

---

## 6. Cleanup (User Ends Session)

```
[UI] User clicked stop button
[AUDIO] 🛑 Stopping audio recorder...
[AUDIO] ✓ Source node disconnected
[AUDIO] ✓ Worklet node disconnected
[AUDIO] ✓ Media track stopped <device_name>
[AUDIO] ✓ AudioContext closed
[AUDIO] ✅ Audio recorder stopped and cleaned up

[AUDIO] 🛑 Stopping audio player...
[AUDIO] ✓ Player worklet disconnected
[AUDIO] ✓ Player AudioContext closed
[AUDIO] ✅ Audio player stopped

[WEBSOCKET] 🔌 Closing connection
[WEBSOCKET] ✓ Connection closed gracefully
[UI] State transition: READY → IDLE
```

---

## 7. Error Scenarios

### Network Disconnect During Conversation
```
[WEBSOCKET] ❌ Connection closed unexpectedly
[WEBSOCKET] Close code: 1006 (Abnormal Closure)
[WEBSOCKET] 🔄 Auto-reconnect triggered
[UI] State transition: SPEAKING → RECONNECTING
[WEBSOCKET] Retry attempt 1/∞ in 5000ms...
```

### Audio Buffer Overflow
```
[AUDIO] ⚠️ Player buffer overflow detected
[AUDIO] Oldest samples will be overwritten
[AUDIO] Buffer health: CRITICAL (>90% full)
```

### Worklet Loading Failure
```
[ERROR] ❌ Failed to load audio worklet
[ERROR] Error: Failed to load module script...
[UI] State transition: CONNECTING_WS → ERROR
```

---

## Testing Checklist

### ✅ Initial Load
- [ ] Page loads without errors
- [ ] "Let's Talk" button is visible
- [ ] Console shows `[UI] VoiceChatScreen mounted`

### ✅ Microphone Access
- [ ] Browser prompts for mic permission
- [ ] Console shows `✓ Microphone access granted`
- [ ] Console shows `✓ AudioContext created`
- [ ] Console shows `✓ Worklet processor loaded`

### ✅ WebSocket Connection
- [ ] Console shows `🔌 Connecting to ws://...`
- [ ] Console shows `✓ Connection opened`
- [ ] UI button changes to "Stop Talking"

### ✅ Audio Recording
- [ ] Speak into microphone
- [ ] Console shows `Received audio chunk: XXXX samples` (every 200ms)
- [ ] Console shows `→ [CLIENT TO AGENT] sent XXXX bytes`
- [ ] No lag or freezing

### ✅ Server Response
- [ ] Console shows `← [AGENT TO CLIENT]`
- [ ] If text: Appears in transcript area
- [ ] If audio: Console shows `Player buffer: XXXX samples added`
- [ ] Audio plays through speakers

### ✅ Turn Complete
- [ ] Console shows `turn_complete: true`
- [ ] State returns to READY
- [ ] Can speak again immediately

### ✅ Cleanup
- [ ] Click "Stop" button
- [ ] Console shows `🛑 Stopping audio recorder`
- [ ] Console shows `✓ AudioContext closed`
- [ ] No resource leaks (check browser DevTools → Performance)

---

## Performance Metrics

Monitor these values in console logs:

| Metric | Expected Value | Warning Threshold |
|--------|---------------|-------------------|
| Audio chunk size | ~3200 samples | <1000 or >10000 |
| Buffer send interval | ~200ms | <100ms or >500ms |
| WebSocket latency | <100ms | >500ms |
| Player buffer fill | 10-50% | >80% |
| Memory growth | Stable | +10MB/min |

---

## Common Issues & Solutions

### Issue: No audio chunks appearing in console
**Solution:**
- Check if mic is muted
- Verify AudioContext state is "running"
- Check browser mic permissions

### Issue: WebSocket won't connect
**Solution:**
- Verify server is running on correct port
- Check CORS settings
- Try ws:// instead of wss:// for local dev

### Issue: Audio plays but sounds distorted
**Solution:**
- Check sample rate mismatch (16kHz vs 24kHz)
- Verify PCM16 conversion
- Check buffer overflow logs

### Issue: State stuck in CONNECTING_WS
**Solution:**
- Check WebSocket URL format
- Verify server accepts is_audio=true parameter
- Check network tab in DevTools

---

## Debug Commands (Browser Console)

```javascript
// Check AudioContext state
window.audioRecorderContext?.state
window.audioPlayerContext?.state

// Force state transition (if exposed)
window.voiceChatDebug?.setState('READY')

// Check buffer health
window.voiceChatDebug?.getBufferHealth()

// Manually trigger cleanup
window.voiceChatDebug?.cleanup()
```

*Note: Debug commands require exposing refs via window object in development mode*
