import { useState, useEffect } from 'react'
import './ConversationsView.css'

const ConversationsView = () => {
  const [conversations, setConversations] = useState([])
  const [selectedTranscript, setSelectedTranscript] = useState(null)

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
        hasTranscript: true,
        transcript: `User: Hello, I need help with my account.
Agent: Hello! I'd be happy to help you with your account. What seems to be the issue?

User: I can't log in to my dashboard. Every time I try, I get an error message.
Agent: I understand how frustrating that must be. Let me help you troubleshoot this issue. Can you tell me what error message you're seeing?

User: It says "Invalid credentials" but I'm sure I'm using the right password.
Agent: I see. Let me check your account status. Can you please provide me with your email address?

User: Sure, it's byewind@example.com
Agent: Thank you. I've found your account. I can see that your account was temporarily locked due to multiple failed login attempts. Let me unlock it for you right now.

User: Oh, I didn't realize that. Thank you so much!
Agent: You're welcome! Your account is now unlocked. Please try logging in again. If you continue to have issues, please don't hesitate to reach out.

User: Perfect! I was able to log in successfully. Thanks for your help!
Agent: Great to hear! Is there anything else I can assist you with today?

User: No, that's all. Have a great day!
Agent: You too! Thank you for contacting support.`
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
        hasTranscript: true,
        transcript: `User: Hi there, I have a question about your pricing plans.
Agent: Hello! I'd be happy to help you with information about our pricing plans. What would you like to know?

User: I'm currently on the basic plan, but I'm interested in upgrading. Can you explain the differences between the plans?
Agent: Absolutely! We have three main plans: Basic, Professional, and Enterprise. The Basic plan includes core features, while Professional adds advanced analytics, priority support, and team collaboration tools.

User: That sounds interesting. What about the Enterprise plan?
Agent: The Enterprise plan includes everything in Professional, plus custom integrations, dedicated account management, SLA guarantees, and unlimited users.

User: How much does the Professional plan cost?
Agent: The Professional plan is $49 per user per month when billed annually, or $59 per month when billed monthly.

User: Can I switch between plans easily?
Agent: Yes! You can upgrade or downgrade at any time. If you upgrade, you'll have immediate access to the new features. If you downgrade, the changes take effect at the start of your next billing cycle.

User: That's good to know. I think I'll upgrade to Professional next month.
Agent: Wonderful! I'll make a note of that. When you're ready, you can upgrade directly from your account settings, or I can help you with the process.

User: Thank you for all the information!
Agent: You're very welcome! Feel free to reach out if you have any other questions.`
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
        hasTranscript: true,
        transcript: `User: Hello? Is anyone there?
Agent: Hello! How can I assist you today?

User: My connection keeps dropping. This is really frustrating.
Agent: I apologize for the inconvenience. Let me help you resolve this connection issue. Can you tell me more about when this started happening?

User: It started about an hour ago. Every few minutes, I get disconnected.
Agent: I understand. Let me check your connection status and network logs.

[Connection interrupted]
[Reconnecting...]

User: See? It just happened again!
Agent: I can see that. I'm analyzing the issue now. It appears there might be a problem with...

[Connection interrupted]
[Unable to reconnect]
[Session ended due to connection failure]`
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
        hasTranscript: true,
        transcript: `User: I'd like to upgrade my subscription to the premium plan.
Agent: Excellent! I can help you with that. What plan are you interested in?

User: I'm looking at the premium plan. Can you tell me more about it?
Agent: Of course! The Premium plan includes all features from the Basic and Professional plans, plus advanced AI capabilities, custom workflows, white-label options, and dedicated support.

User: That sounds perfect for what I need. How does the billing work?
Agent: The Premium plan is $99 per user per month when billed annually, which saves you about 20% compared to monthly billing at $119 per month.

User: I'd like to go with the annual billing. What's the process?
Agent: Great choice! I'll walk you through the upgrade process. First, I'll need to update your subscription. You'll be charged a prorated amount for the remainder of this billing cycle.

User: That makes sense. Will I lose any of my current data or settings?
Agent: Not at all! All your data, settings, and configurations will remain exactly as they are. You'll simply gain access to the additional Premium features immediately after the upgrade.

User: Perfect. Let's proceed with the upgrade.
Agent: Wonderful! I'm processing the upgrade now... Done! Your account has been successfully upgraded to Premium.

User: That was quick! When will I see the new features?
Agent: They're available right now! You should see new menu options and features when you refresh your dashboard. I recommend checking out our Premium onboarding guide to make the most of your new features.

User: Great! One more question - what's your cancellation policy if I need to downgrade later?
Agent: You can downgrade or cancel at any time. For annual plans, you'll retain Premium access until the end of your billing period. We also offer a 30-day money-back guarantee if you're not satisfied.

User: That's very reassuring. Thank you so much for your help!
Agent: You're very welcome! Congratulations on upgrading to Premium. If you have any questions about the new features, our Premium support team is available 24/7. Enjoy!

User: Will do. Have a great day!
Agent: You too! Thank you for your business.`
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
        hasTranscript: true,
        transcript: `User: Can you help me with a technical issue?
Agent: Of course! Please describe the issue you're experiencing.

User: My files aren't syncing properly between devices.
Agent: I'd be happy to help you resolve the syncing issue. Let me gather some information first. Which devices are you having trouble syncing between?

User: My laptop and my phone.
Agent: Thank you. Have you tried refreshing the sync manually from the settings menu?`
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

  const openTranscriptModal = (transcript) => {
    setSelectedTranscript(transcript)
  }

  const closeTranscriptModal = () => {
    setSelectedTranscript(null)
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
                  <button
                    className="transcript-button"
                    onClick={() => openTranscriptModal(conversation.transcript)}
                  >
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

export default ConversationsView