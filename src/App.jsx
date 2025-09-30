import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ConversationsView from './components/ConversationsView'
import LiveEventsView from './components/LiveEventsView'
import VoiceChatScreen from './components/voice-chat/VoiceChatScreen'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('voice-chat')

  return (
    <div className="app">
      {activeView !== 'voice-chat' && (
        <Sidebar activeView={activeView} setActiveView={setActiveView} />
      )}
      <main className="main-content">
        {activeView === 'voice-chat' && <VoiceChatScreen />}
        {activeView === 'conversations' && <ConversationsView />}
        {activeView === 'live-events' && <LiveEventsView />}
      </main>
    </div>
  )
}

export default App