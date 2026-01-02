console.log("main.jsx is executing"); // Add this as the first line

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { ConversationProvider } from './contexts/ConversationContext'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ConversationProvider>
      <App />
    </ConversationProvider>
  </StrictMode>,
)
