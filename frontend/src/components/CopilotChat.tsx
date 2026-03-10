/**
 * Copilot Chat Component
 * Main chat interface with message display and interaction
 */

import { useEffect, useRef, useMemo } from 'react'
import { Trash2, Download } from 'lucide-react'
import { ChatMessage } from './ChatMessage'
import { CopilotResponse } from './CopilotResponse'
import { SuggestedQuestions } from './SuggestedQuestions'
import { MessageInput } from './MessageInput'
import { Button } from './ui/Button'
import { Alert } from './ui/Alert'
import { Spinner } from './ui/Spinner'
import { Card } from './ui/Card'
import { SUGGESTED_QUESTIONS_LIST } from '../hooks/useCopilot'
import type { ChatMessage as ChatMessageType } from '../types/copilot'

interface CopilotChatProps {
  messages: ChatMessageType[]
  isLoading: boolean
  error: string | null
  onSendMessage: (question: string) => Promise<void>
  onClearChat: () => void
  onExport: () => void
}

export function CopilotChat({
  messages,
  isLoading,
  error,
  onSendMessage,
  onClearChat,
  onExport
}: CopilotChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Group messages with their responses
  const groupedMessages = useMemo(() => {
    const groups: Array<{
      userMessage: ChatMessageType
      assistantMessages: ChatMessageType[]
    }> = []

    let currentGroup: {
      userMessage: ChatMessageType
      assistantMessages: ChatMessageType[]
    } | null = null

    messages.forEach(msg => {
      if (msg.role === 'user') {
        if (currentGroup) {
          groups.push(currentGroup)
        }
        currentGroup = {
          userMessage: msg,
          assistantMessages: []
        }
      } else if (msg.role === 'assistant' && currentGroup) {
        currentGroup.assistantMessages.push(msg)
      }
    })

    if (currentGroup) {
      groups.push(currentGroup)
    }

    return groups
  }, [messages])

  // Determine if we should show suggested questions
  const showSuggestedQuestions = messages.length === 0

  // Handle navigation to citation source
  const handleCitationNavigate = (link: string) => {
    window.location.href = link
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-slate-900 to-slate-950">
      {/* Header */}
      <div className="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-slate-800/50">
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white">Copilot Assistant</h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
            Ask questions about your energy data and sustainability metrics
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={onExport}
            disabled={messages.length === 0}
            aria-label="Export conversation"
            title="Export as JSON"
            className="hidden sm:flex"
          >
            <Download className="w-4 h-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={onClearChat}
            disabled={messages.length === 0}
            aria-label="Clear chat"
            title="Clear all messages"
          >
            <Trash2 className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">Clear</span>
          </Button>
        </div>
      </div>

      {/* Messages Container */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4"
        role="region"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.length === 0 && !showSuggestedQuestions && (
          <div className="flex items-center justify-center h-full">
            <Spinner size="lg" color="primary" message="Starting conversation..." />
          </div>
        )}

        {groupedMessages.map((group, groupIndex) => (
          <div key={`group-${groupIndex}`} className="space-y-3">
            {/* User Message */}
            <ChatMessage message={group.userMessage} />

            {/* Assistant Messages */}
            {group.assistantMessages.map(msg => (
              <div key={msg.id}>
                {msg.loading ? (
                  <div className="flex items-start gap-3 mb-4">
                    <div className="flex-shrink-0 mt-1">
                      <Spinner size="sm" color="primary" />
                    </div>
                    <div className="text-sm text-slate-400">Analyzing your question...</div>
                  </div>
                ) : (
                  <Card className="bg-slate-800/50 border-slate-700/50">
                    <div className="p-4 sm:p-6">
                      <CopilotResponse
                        message={msg.content}
                        citations={msg.citations}
                        error={msg.error}
                        onCitationNavigate={handleCitationNavigate}
                      />
                    </div>
                  </Card>
                )}
              </div>
            ))}
          </div>
        ))}

        {/* Error Alert */}
        {error && (
          <Alert
            variant="error"
            title="Error"
            message={error}
            onClose={() => {
              // Error will be cleared on next successful message
            }}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Section */}
      <div className="border-t border-slate-800/50 px-4 sm:px-6 py-4 bg-slate-950/50">
        {/* Suggested Questions */}
        {showSuggestedQuestions && (
          <div className="mb-4">
            <SuggestedQuestions
              questions={SUGGESTED_QUESTIONS_LIST}
              onQuestionClick={onSendMessage}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* Message Input */}
        <MessageInput
          onSend={onSendMessage}
          isLoading={isLoading}
          autoFocus={true}
        />

        {/* Info Text */}
        <p className="text-xs text-slate-500 mt-3 text-center">
          Citations may include metrics, reports, and evidence from your sustainability data.
        </p>
      </div>
    </div>
  )
}
