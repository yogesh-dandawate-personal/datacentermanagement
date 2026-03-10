/**
 * Copilot Hook
 * Custom hook for managing copilot chat interactions and state
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { ChatMessage, ConversationHistory, CopilotResponse } from '../types/copilot'
import api from '../services/api'

interface UseCopilotState {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  conversations: ConversationHistory[]
  currentConversationId: string | null
}

export interface UseCopilotReturn extends UseCopilotState {
  sendMessage: (question: string) => Promise<void>
  clearChat: () => void
  deleteConversation: (id: string) => void
  loadConversation: (id: string) => void
  exportConversation: () => void
  loadHistory: () => Promise<void>
}

// Default suggested questions
const SUGGESTED_QUESTIONS = [
  {
    id: '1',
    text: 'What is our Scope 2 emissions this month?',
    category: 'emissions'
  },
  {
    id: '2',
    text: 'How are we performing against our PUE target?',
    category: 'efficiency'
  },
  {
    id: '3',
    text: 'What evidence do we have for our carbon calculations?',
    category: 'evidence'
  },
  {
    id: '4',
    text: 'Show me our energy consumption trends',
    category: 'trends'
  }
]

export function useCopilot(): UseCopilotReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversations, setConversations] = useState<ConversationHistory[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const messageIdCounterRef = useRef(0)

  // Load chat history from localStorage on mount
  useEffect(() => {
    loadHistory()
  }, [])

  // Generate unique message IDs
  const generateMessageId = useCallback(() => {
    return `msg-${Date.now()}-${++messageIdCounterRef.current}`
  }, [])

  // Load conversation history from API or localStorage
  const loadHistory = useCallback(async () => {
    try {
      // Try to load from API first (when backend is available)
      const response = await api.get('/copilot/history')
      if (response) {
        setConversations(response as ConversationHistory[])
        return
      }
    } catch (err) {
      // Fall back to localStorage
      console.warn('Failed to load history from API, using localStorage')
    }

    // Load from localStorage as fallback
    const stored = localStorage.getItem('copilot_conversations')
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ConversationHistory[]
        setConversations(parsed)
      } catch (e) {
        console.error('Failed to parse stored conversations', e)
      }
    }
  }, [])

  // Save conversation to localStorage
  const saveConversation = useCallback((conversation: ConversationHistory) => {
    setConversations(prev => {
      const updated = prev.some(c => c.id === conversation.id)
        ? prev.map(c => c.id === conversation.id ? conversation : c)
        : [...prev, conversation]

      // Save to localStorage
      localStorage.setItem('copilot_conversations', JSON.stringify(updated))
      return updated
    })
  }, [])

  // Send a message to the copilot API
  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim()) return

    try {
      setError(null)
      setIsLoading(true)

      // Create user message
      const userMessageId = generateMessageId()
      const userMessage: ChatMessage = {
        id: userMessageId,
        role: 'user',
        content: question,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, userMessage])

      // Create loading assistant message
      const assistantLoadingId = generateMessageId()
      const assistantLoadingMessage: ChatMessage = {
        id: assistantLoadingId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        loading: true
      }

      setMessages(prev => [...prev, assistantLoadingMessage])

      // Call copilot API
      const response = await api.post('/copilot/ask', { question })

      if (!response) {
        throw new Error('No response from API')
      }

      const copilotResponse = response as CopilotResponse

      // Create assistant message with citations
      const assistantMessage: ChatMessage = {
        id: assistantLoadingId,
        role: 'assistant',
        content: copilotResponse.message,
        timestamp: new Date(),
        citations: copilotResponse.citations,
        loading: false,
        error: copilotResponse.errorMessage
      }

      setMessages(prev =>
        prev.map(m => m.id === assistantLoadingId ? assistantMessage : m)
      )

      // Save to current conversation or create new one
      if (currentConversationId) {
        const conversation = conversations.find(c => c.id === currentConversationId)
        if (conversation) {
          conversation.messages = [userMessage, assistantMessage]
          conversation.updatedAt = new Date()
          saveConversation(conversation)
        }
      } else {
        // Create new conversation
        const newConversationId = `conv-${Date.now()}`
        const newConversation: ConversationHistory = {
          id: newConversationId,
          title: question.substring(0, 50) + (question.length > 50 ? '...' : ''),
          messages: [userMessage, assistantMessage],
          createdAt: new Date(),
          updatedAt: new Date()
        }
        setCurrentConversationId(newConversationId)
        saveConversation(newConversation)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'
      setError(errorMessage)

      // Update the loading message with error
      setMessages(prev =>
        prev.map(m =>
          m.loading
            ? { ...m, loading: false, error: errorMessage, content: "Sorry, I couldn't process that request. Please try again." }
            : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [currentConversationId, conversations, generateMessageId, saveConversation])

  // Clear current chat
  const clearChat = useCallback(() => {
    setMessages([])
    setCurrentConversationId(null)
    setError(null)
    messageIdCounterRef.current = 0
  }, [])

  // Delete a conversation
  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => {
      const updated = prev.filter(c => c.id !== id)
      localStorage.setItem('copilot_conversations', JSON.stringify(updated))
      return updated
    })

    if (currentConversationId === id) {
      clearChat()
    }
  }, [currentConversationId, clearChat])

  // Load a specific conversation
  const loadConversation = useCallback((id: string) => {
    const conversation = conversations.find(c => c.id === id)
    if (conversation) {
      setCurrentConversationId(id)
      setMessages(conversation.messages)
      setError(null)
    }
  }, [conversations])

  // Export conversation as JSON/PDF
  const exportConversation = useCallback(() => {
    if (messages.length === 0) {
      setError('No messages to export')
      return
    }

    const conversation = {
      title: currentConversationId ? conversations.find(c => c.id === currentConversationId)?.title : 'Chat Export',
      exportedAt: new Date().toISOString(),
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp,
        citations: m.citations
      }))
    }

    const dataStr = JSON.stringify(conversation, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)

    const exportFileDefaultName = `copilot-export-${Date.now()}.json`
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }, [messages, currentConversationId, conversations])

  return {
    messages,
    isLoading,
    error,
    conversations,
    currentConversationId,
    sendMessage,
    clearChat,
    deleteConversation,
    loadConversation,
    exportConversation,
    loadHistory
  }
}

export const SUGGESTED_QUESTIONS_LIST = SUGGESTED_QUESTIONS
