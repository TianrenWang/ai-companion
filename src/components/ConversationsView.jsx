import { useState, useEffect } from 'react'
import './ConversationsView.css'

const ConversationsView = () => {
  const [conversations, setConversations] = useState([])

  useEffect(() => {
    // TODO: Replace with actual API call to fetch conversations data
    // This is where your backend colleagues will plug in the data source
    const mockData = [
      {
        id: 1,
        user: {
          name: 'ByeWind',
          avatar: null,
          initials: 'BW'
        },
        dateTime: 'Jun 24, 2025 - 9:45',
        duration: '0:37 seconds',
        status: 'in_progress',
        hasTranscript: true
      },
      {
        id: 2,
        user: {
          name: 'Natali Craig',
          avatar: null,
          initials: 'NC'
        },
        dateTime: 'Mar 10, 2025 - 10:45',
        duration: '5:07 minutes',
        status: 'completed',
        hasTranscript: true
      },
      {
        id: 3,
        user: {
          name: 'Drew Cano',
          avatar: null,
          initials: 'DC'
        },
        dateTime: 'Nov 10, 2025 - 2:45',
        duration: '5:07 minutes',
        status: 'failed',
        hasTranscript: true
      },
      {
        id: 4,
        user: {
          name: 'Orlando Diggs',
          avatar: null,
          initials: 'OD'
        },
        dateTime: 'Dec 20, 2025 - 8:30',
        duration: '10:07 minutes',
        status: 'completed',
        hasTranscript: true
      },
      {
        id: 5,
        user: {
          name: 'Andi Lane',
          avatar: null,
          initials: 'AL'
        },
        dateTime: 'Jul 25, 2025 - 10:05',
        duration: '1:03 minutes',
        status: 'unknown',
        hasTranscript: true
      }
    ]

    setConversations(mockData)
  }, [])

  const getStatusClass = (status) => {
    switch (status) {
      case 'in_progress':
        return 'status-progress'
      case 'completed':
        return 'status-completed'
      case 'failed':
        return 'status-failed'
      default:
        return 'status-unknown'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'in_progress':
        return 'In Progress'
      case 'completed':
        return 'Green'
      case 'failed':
        return 'Red'
      default:
        return 'N/A'
    }
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }

  return (
    <div className="conversations-view">
      <h1 className="page-title">Conversations</h1>
      
      <div className="conversations-table">
        <div className="table-header">
          <div className="header-cell user-column">User</div>
          <div className="header-cell date-column">Date & Time</div>
          <div className="header-cell duration-column">Duration</div>
          <div className="header-cell status-column">Status</div>
          <div className="header-cell transcript-column">Transcript</div>
        </div>

        <div className="table-body">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="table-row">
              <div className="cell user-column">
                <div className="user-info">
                  <div className="user-avatar">
                    {conversation.user.avatar ? (
                      <img src={conversation.user.avatar} alt={conversation.user.name} />
                    ) : (
                      <span className="avatar-initials">{getInitials(conversation.user.name)}</span>
                    )}
                  </div>
                  <span className="user-name">{conversation.user.name}</span>
                </div>
              </div>
              
              <div className="cell date-column">{conversation.dateTime}</div>
              
              <div className="cell duration-column">{conversation.duration}</div>
              
              <div className="cell status-column">
                <span className={`status-badge ${getStatusClass(conversation.status)}`}>
                  {getStatusText(conversation.status)}
                </span>
              </div>
              
              <div className="cell transcript-column">
                {conversation.hasTranscript && (
                  <button className="transcript-button">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 7h12M4 10h12M4 13h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                    </svg>
                    Transcript
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ConversationsView