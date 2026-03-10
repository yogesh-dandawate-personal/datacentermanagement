# Copilot Chat UI Implementation Guide

## Overview

The Copilot Chat UI is a comprehensive AI-powered conversational interface for querying sustainability and energy data. It provides an intuitive chat experience with cited responses, conversation history management, and mobile-responsive design.

## Architecture

### File Structure

```
frontend/src/
├── pages/
│   └── Copilot.tsx                 # Main copilot page with sidebar and history
├── components/
│   ├── CopilotChat.tsx             # Core chat interface component
│   ├── ChatMessage.tsx             # Individual message display
│   ├── CopilotResponse.tsx         # Response with citations and confidence
│   ├── CitationCard.tsx            # Expandable citation details
│   ├── SuggestedQuestions.tsx       # Quick action buttons for questions
│   └── MessageInput.tsx            # Input field with auto-save
├── hooks/
│   └── useCopilot.ts               # State management and API integration
└── types/
    └── copilot.ts                  # TypeScript types and interfaces
```

## Components

### 1. Copilot Page (`pages/Copilot.tsx`)

The main page component that provides:
- Full-screen layout with responsive design
- Sidebar for conversation history
- Search/filter conversations
- Delete conversations
- New conversation button
- Clear all history
- Mobile-responsive sidebar with collapsible menu

**Key Features:**
- Responsive sidebar (collapsible on mobile)
- Conversation search
- Quick navigation between conversations
- Delete individual or all conversations
- Auto-close sidebar on mobile when selecting conversation

### 2. CopilotChat Component (`components/CopilotChat.tsx`)

Core chat interface that displays:
- Message thread with auto-scrolling
- Loading states and typing indicators
- Suggested questions for new conversations
- Message input area
- Export functionality
- Clear chat button
- Error alerts

**Props:**
```typescript
interface CopilotChatProps {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  onSendMessage: (question: string) => Promise<void>
  onClearChat: () => void
  onExport: () => void
}
```

### 3. ChatMessage Component (`components/ChatMessage.tsx`)

Displays individual messages with:
- User messages (right-aligned, blue background)
- Assistant messages (left-aligned, gray background)
- Typing indicator for loading states
- Copy-to-clipboard button
- Timestamps
- Error message styling

**Props:**
```typescript
interface ChatMessageProps {
  message: ChatMessage
}
```

### 4. CopilotResponse Component (`components/CopilotResponse.tsx`)

Shows assistant responses with:
- Main message text
- Confidence score with visual bar
- Citations list (if available)
- Error messaging
- Low-confidence warnings
- Citation count

**Props:**
```typescript
interface CopilotResponseProps {
  message: string
  citations?: Citation[]
  confidence?: number
  error?: string
  onCitationNavigate?: (link: string) => void
}
```

### 5. CitationCard Component (`components/CitationCard.tsx`)

Expandable citation details showing:
- Citation type badge (metric, report, evidence, document)
- Confidence score
- Citation name and value
- Expandable section with:
  - Full description
  - Source information
  - Date
  - Owner/creator
  - "View Source" navigation button
- Color-coded by type
- Click to expand/collapse

**Citation Types:**
- `metric`: KPI and measurement data
- `report`: Reports and documents
- `evidence`: Supporting evidence
- `document`: General documents

### 6. SuggestedQuestions Component (`components/SuggestedQuestions.tsx`)

Quick action buttons displaying:
- Pre-defined suggested questions
- Grid layout (responsive)
- Disabled state during loading
- Hover effects
- Tooltip on hover

### 7. MessageInput Component (`components/MessageInput.tsx`)

Smart input field with:
- Text input with placeholder
- Send button
- Keyboard shortcut (Ctrl+Enter or Cmd+Enter)
- Auto-save draft to localStorage
- Load draft on mount
- Disabled state during loading
- Keyboard hint display
- Character input feedback

**Features:**
- Auto-save draft after 500ms delay
- Persists draft to localStorage
- Loads draft on page reload
- Clears draft after sending
- Touch-friendly on mobile

## Custom Hook: useCopilot

The `useCopilot` hook manages all chat state and API interactions:

```typescript
export function useCopilot(): UseCopilotReturn {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  conversations: ConversationHistory[]
  currentConversationId: string | null

  sendMessage: (question: string) => Promise<void>
  clearChat: () => void
  deleteConversation: (id: string) => void
  loadConversation: (id: string) => void
  exportConversation: () => void
  loadHistory: () => Promise<void>
}
```

### State Management

- **messages**: Current conversation messages
- **isLoading**: Loading state during API call
- **error**: Error message if request fails
- **conversations**: All stored conversations
- **currentConversationId**: Currently active conversation ID

### API Integration

The hook integrates with the backend via:
- `POST /api/v1/copilot/ask` - Send question and get response
- `GET /api/v1/copilot/history` - Load conversation history

Fallback to localStorage if API is unavailable.

### Key Functions

**sendMessage(question)**
- Sends user question to copilot API
- Creates loading message
- Updates message on response
- Auto-saves to current conversation or creates new
- Handles errors gracefully

**loadHistory()**
- Loads conversations from API or localStorage
- Called on component mount
- Used to restore conversation list

**clearChat()**
- Clears current conversation
- Resets state for new chat

**deleteConversation(id)**
- Removes conversation from list
- Clears chat if active conversation
- Persists to localStorage

**loadConversation(id)**
- Loads specific conversation
- Updates message list
- Clears error state

**exportConversation()**
- Exports current chat as JSON file
- Downloads to user's computer
- Includes metadata and timestamps

## Type Definitions

```typescript
interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  citations?: Citation[]
  loading?: boolean
  error?: string
}

interface Citation {
  id: string
  type: 'metric' | 'report' | 'evidence' | 'document'
  name: string
  value?: string | number
  unit?: string
  source?: string
  date?: string
  confidence?: number
  link?: string
  description?: string
  owner?: string
}

interface ConversationHistory {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

interface CopilotResponse {
  message: string
  citations: Citation[]
  confidence: number
  hasError?: boolean
  errorMessage?: string
}
```

## Features

### Message Display
- Auto-scroll to latest message
- Typing indicator while waiting for response
- Copy-to-clipboard for assistant messages
- Timestamp on each message
- Error message styling with fallback text

### Conversation Management
- Auto-create new conversation on first message
- Search conversations by title
- View conversation metadata (message count, date)
- Delete individual conversations
- Delete all conversations with confirmation
- Persistent storage in localStorage

### Suggested Questions
Four default suggested questions:
1. "What is our Scope 2 emissions this month?"
2. "How are we performing against our PUE target?"
3. "What evidence do we have for our carbon calculations?"
4. "Show me our energy consumption trends"

Questions are shown only for new conversations.

### Citations
- Inline citations in response
- Expandable cards with details
- Confidence score (0-100%)
- Color-coded by type
- Direct navigation to source
- Meta information (owner, date)

### Error Handling
- API failure fallback messaging
- Low-confidence warnings
- Partial results support
- Graceful degradation
- User-friendly error messages
- Toast notifications

### Mobile Responsive
- Full-height chat on mobile
- Collapsible sidebar
- Touch-friendly buttons
- Swipe-friendly layout
- Optimized input field
- Responsive grid for suggestions

## API Integration

### Backend Endpoints

**Ask Copilot**
```
POST /api/v1/copilot/ask
Request: { question: string }
Response: {
  message: string
  citations: Citation[]
  confidence: number
  errorMessage?: string
}
```

**Get History**
```
GET /api/v1/copilot/history
Response: ConversationHistory[]
```

### Error Handling

The hook handles errors gracefully:
- Network errors show "Failed to send message"
- API errors show server error message
- Messages display with error state
- Loading indicator replaced with error text
- Error persists until next successful message

### Offline Support

- LocalStorage fallback for conversation history
- Draft auto-save for offline typing
- Error messages if API unavailable
- Cache management

## Styling

### Design Tokens
- Chat bubbles: `bg-primary-600` (user), `bg-slate-800` (assistant)
- Citation cards: Type-specific colors (blue, purple, green, amber)
- Confidence: Green (>80%), Yellow (60-80%), Red (<60%)
- Buttons: Primary, secondary, outline, ghost, danger variants
- Responsive spacing using Tailwind

### Dark Mode
- Full dark mode support
- High contrast text
- Optimized for readability
- Smooth transitions

## Accessibility

### WCAG 2.1 AA Compliance
- ARIA labels on all buttons
- Keyboard navigation (Tab through messages)
- Screen reader support for citations
- Color not-only indicators (icons + text)
- Sufficient text contrast (4.5:1)
- Focus indicators on interactive elements
- Live region for new messages

### Keyboard Navigation
- Tab: Navigate through interactive elements
- Ctrl/Cmd+Enter: Send message
- Escape: Close dialogs
- Arrow keys: Expand/collapse citations

## Performance

### Optimizations
- Lazy load conversation history
- Virtualize long message lists (future)
- Debounce input changes (500ms for draft save)
- Cache API responses in localStorage
- Minimize re-renders with React.memo
- Efficient state management

### Bundle Impact
- ~15KB gzipped for new components
- Lazy load with code splitting
- Tree-shaking compatible
- No additional runtime dependencies

## Usage Example

```typescript
import { Copilot } from './pages/Copilot'

// In App.tsx routes
<Route
  path="/copilot"
  element={
    <ProtectedRoute>
      <Layout>
        <Copilot />
      </Layout>
    </ProtectedRoute>
  }
/>
```

In navigation:
```typescript
// Layout.tsx navItems
{ icon: MessageSquare, label: 'Copilot', href: '/copilot', color: 'text-pink-400' }
```

## Future Enhancements

1. **Streaming Responses**: Real-time message streaming for faster feedback
2. **Voice Input**: Speech-to-text for hands-free input
3. **Message Reactions**: Emoji reactions to messages
4. **Thread Replies**: Nested conversations
5. **User Mentions**: @mentions for collaboration
6. **Rich Media**: Image/file uploads in chat
7. **Analytics**: Usage tracking and insights
8. **Customization**: User-defined suggested questions
9. **AI Fine-tuning**: Conversation-based model learning
10. **Multi-language**: i18n support

## Testing

### Unit Tests
- Component rendering
- Hook state management
- API error handling
- LocalStorage persistence
- Citation expansion

### Integration Tests
- Full chat flow
- Conversation persistence
- History management
- Export functionality

### E2E Tests
- User interactions
- Keyboard navigation
- Mobile responsiveness
- Error scenarios

## Troubleshooting

### Messages Not Sending
1. Check API endpoint: `POST /api/v1/copilot/ask`
2. Verify authentication token
3. Check network tab in DevTools
4. Review backend logs

### Citations Not Displaying
1. Verify API response includes citations array
2. Check citation object structure
3. Review console for parsing errors

### Draft Not Saving
1. Check localStorage availability
2. Verify localStorage isn't full
3. Check browser settings for storage restrictions

### Performance Issues
1. Limit conversation history display
2. Implement message virtualization
3. Clear very old conversations
4. Check API response time

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Dependencies

- React 18+
- TypeScript
- TailwindCSS
- Lucide React (icons)
- React Router
- Fetch API

## Migration Notes

When integrating with existing chat systems:
1. Update API endpoints to match your backend
2. Customize suggested questions
3. Update citation types as needed
4. Adjust styling to match brand colors
5. Configure error handling

---

**Version**: 1.0.0
**Last Updated**: 2026-03-10
**Status**: Production Ready
