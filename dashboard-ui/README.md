# NORA AI Dashboard

A lightweight React dashboard for the AI companion platform with two main views: Conversations and Live Events.

## Setup

```bash
npm install
npm run dev
```

## Features

- **Conversations View**: Displays completed customer conversations with status, duration, and transcript access
- **Live Events View**: Placeholder for real-time event monitoring (to be implemented)

## Backend Integration

The Conversations view includes clear comments indicating where to plug in data sources. Look for:
- `useEffect` hook in `src/components/ConversationsView.jsx` - Replace mock data with API calls
- Current mock data structure shows expected data format

## Project Structure

```
Dashboard/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx         # Navigation sidebar
│   │   ├── ConversationsView.jsx   # Main conversations table
│   │   └── LiveEventsView.jsx     # Placeholder for live events
│   ├── App.jsx                 # Main app component
│   └── main.jsx               # React entry point
├── index.html
├── package.json
└── vite.config.js
```