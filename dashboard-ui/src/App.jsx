import { useState } from 'react'
import Sidebar from './components/Sidebar'
import ConversationsView from './components/ConversationsView'
import LiveEventsView from './components/LiveEventsView'
import './App.css'

function App() {
  const [activeView, setActiveView] = useState('conversations')

  return (
    <div className="app">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <main className="main-content">
        {activeView === 'conversations' ? <ConversationsView /> : <LiveEventsView />}
      </main>
    </div>
  )
}

export default App