/**
 * Copilot Chat Types
 * Type definitions for the copilot chat system
 */

export interface Citation {
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

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  citations?: Citation[]
  loading?: boolean
  error?: string
}

export interface ConversationHistory {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface CopilotResponse {
  message: string
  citations: Citation[]
  confidence: number
  hasError?: boolean
  errorMessage?: string
}

export interface CopilotQuestion {
  id: string
  text: string
  category?: string
}

export interface ChatState {
  messages: ChatMessage[]
  conversations: ConversationHistory[]
  currentConversationId?: string
  isLoading: boolean
  error: string | null
}
