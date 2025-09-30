import './Sidebar.css'

const Sidebar = ({ activeView, setActiveView }) => {
  return (
    <aside className="sidebar">
      <div className="logo">
        <span className="logo-text">NORA</span>
      </div>
      
      <nav className="navigation">
        <button
          className={`nav-item ${activeView === 'live-events' ? 'active' : ''}`}
          onClick={() => setActiveView('live-events')}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 10l7-7v4h7v6h-7v4l-7-7z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
          </svg>
          <span>Live Events</span>
        </button>
        
        <button
          className={`nav-item ${activeView === 'conversations' ? 'active' : ''}`}
          onClick={() => setActiveView('conversations')}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 12h4M8 8h4M6 16h8a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span>Conversations</span>
        </button>
      </nav>
    </aside>
  )
}

export default Sidebar