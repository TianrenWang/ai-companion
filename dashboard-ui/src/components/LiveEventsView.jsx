import { useState, useEffect } from 'react'
import './LiveEventsView.css'

const LiveEventsView = () => {
  const [events, setEvents] = useState([])
  const [selectedTranscript, setSelectedTranscript] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)
  const [users, setUsers] = useState([])
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  useEffect(() => {
    // TODO: Replace with actual API call to fetch users and events data
    const mockUsers = [
      { id: 1, name: 'Sara M.', avatar: null, initials: 'SM' },
      { id: 2, name: 'John Smith', avatar: null, initials: 'JS' },
      { id: 3, name: 'Sarah Johnson', avatar: null, initials: 'SJ' },
      { id: 4, name: 'Mike Brown', avatar: null, initials: 'MB' },
      { id: 5, name: 'Emily Davis', avatar: null, initials: 'ED' },
      { id: 6, name: 'David Wilson', avatar: null, initials: 'DW' }
    ]

    const allEvents = {
      1: [
        {
          id: 1,
          userId: 1,
          timestamp: '2025-09-30 14:23:15',
          status: 'green',
          action: 'ALLOW',
          transcript: 'User: Hello, I need help with my account.\nAgent: Hello! I\'d be happy to help you with your account. What seems to be the issue?\nUser: I can\'t log in to my dashboard.\nAgent: I understand. Let me help you troubleshoot this issue.'
        },
        {
          id: 2,
          userId: 1,
          timestamp: '2025-09-30 14:22:48',
          status: 'orange',
          action: 'WARN',
          transcript: 'User: Hi there, I have a question about pricing.\nAgent: Hi! I\'ll be right with you.\nUser: Thank you, I\'ll wait.'
        },
        {
          id: 3,
          userId: 1,
          timestamp: '2025-09-30 14:21:32',
          status: 'red',
          action: 'BLOCK',
          transcript: 'User: Hello?\nAgent: Hello! How can I assist you today?\nUser: My connection keeps dropping.\n[Connection interrupted]'
        },
        {
          id: 4,
          userId: 1,
          timestamp: '2025-09-30 14:20:15',
          status: 'green',
          action: 'ALLOW',
          transcript: 'User: I\'d like to upgrade my subscription.\nAgent: Excellent! I can help you with that. What plan are you interested in?\nUser: I\'m looking at the premium plan.\nAgent: Great choice! Let me walk you through the features.'
        },
        {
          id: 5,
          userId: 1,
          timestamp: '2025-09-30 14:19:50',
          status: 'orange',
          action: 'ESCALATE',
          transcript: 'User: Can you help me with a technical issue?\nAgent: Of course! Please describe the issue you\'re experiencing.\nUser: My files aren\'t syncing properly.'
        }
      ]
    }

    setUsers(mockUsers)
    setSelectedUser(mockUsers[0])
    setEvents(allEvents[1])
  }, [])

  const getStatusClass = (status) => {
    switch (status) {
      case 'green':
        return 'status-green'
      case 'orange':
        return 'status-orange'
      case 'red':
        return 'status-red'
      default:
        return 'status-unknown'
    }
  }

  const getActionClass = (action) => {
    switch (action) {
      case 'ALLOW':
        return 'action-allow'
      case 'WARN':
        return 'action-warn'
      case 'BLOCK':
        return 'action-block'
      case 'ESCALATE':
        return 'action-escalate'
      default:
        return 'action-default'
    }
  }

  const openTranscriptModal = (transcript) => {
    setSelectedTranscript(transcript)
  }

  const closeTranscriptModal = () => {
    setSelectedTranscript(null)
  }

  const handleUserSelect = (user) => {
    setSelectedUser(user)
    setIsDropdownOpen(false)
    // TODO: Fetch events for the selected user
  }

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen)
  }

  return (
    <div className="live-events-view">
      <h1 className="page-title">Live Events</h1>

      {/* User Selection Dropdown */}
      <div className="user-selector-container">
        <div className="user-selector" onClick={toggleDropdown}>
          <div className="selected-user">
            <div className="user-avatar">
              {selectedUser?.avatar ? (
                <img src={selectedUser.avatar} alt={selectedUser.name} />
              ) : (
                <span className="avatar-initials">{selectedUser?.initials}</span>
              )}
            </div>
            <span className="user-name">{selectedUser?.name}</span>
          </div>
          <svg
            className={`dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        {isDropdownOpen && (
          <div className="dropdown-menu">
            {users.map((user) => (
              <div
                key={user.id}
                className={`dropdown-item ${selectedUser?.id === user.id ? 'active' : ''}`}
                onClick={() => handleUserSelect(user)}
              >
                <div className="user-avatar">
                  {user.avatar ? (
                    <img src={user.avatar} alt={user.name} />
                  ) : (
                    <span className="avatar-initials">{user.initials}</span>
                  )}
                </div>
                <span className="user-name">{user.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="events-table">
        <div className="table-header">
          <div className="header-cell timestamp-column">Timestamp</div>
          <div className="header-cell status-column">Status</div>
          <div className="header-cell action-column">Action</div>
          <div className="header-cell messages-column">Messages</div>
        </div>

        <div className="table-body">
          {events.map((event) => (
            <div key={event.id} className="table-row">
              <div className="cell timestamp-column">{event.timestamp}</div>

              <div className="cell status-column">
                <span className={`status-indicator ${getStatusClass(event.status)}`}></span>
              </div>

              <div className="cell action-column">
                <span className={`action-pill ${getActionClass(event.action)}`}>
                  {event.action}
                </span>
              </div>

              <div className="cell messages-column">
                <button
                  className="transcript-button"
                  onClick={() => openTranscriptModal(event.transcript)}
                >
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M4 7h12M4 10h12M4 13h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                  Transcript
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedTranscript && (
        <div className="modal-overlay" onClick={closeTranscriptModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Conversation Transcript</h2>
              <button className="close-button" onClick={closeTranscriptModal}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <pre className="transcript-text">{selectedTranscript}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LiveEventsView