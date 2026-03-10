/**
 * Chat Message Component
 * Displays individual chat messages with user/assistant styling
 */

import { Copy, CheckCircle2 } from 'lucide-react'
import { useState, useCallback } from 'react'
import { ChatMessage as ChatMessageType } from '../types/copilot'
import { Button } from './ui/Button'
import { Spinner } from './ui/Spinner'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [message.content])

  const isUser = message.role === 'user'
  const isAssistant = message.role === 'assistant'

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      role={isAssistant ? 'status' : 'article'}
      aria-live={message.loading ? 'polite' : 'off'}
    >
      <div
        className={`
          max-w-xs lg:max-w-md xl:max-w-lg rounded-lg px-4 py-3
          ${isUser
            ? 'bg-primary-600 text-white rounded-br-none'
            : 'bg-slate-800/80 text-slate-100 rounded-bl-none border border-slate-700/50'
          }
        `}
      >
        {message.loading ? (
          <div className="flex items-center gap-2">
            <Spinner size="sm" color={isUser ? 'white' : 'primary'} />
            <span className="text-sm">Thinking...</span>
          </div>
        ) : (
          <>
            <div className="break-words text-sm leading-relaxed">
              {message.error ? (
                <div className="text-yellow-200">
                  <p className="font-medium mb-1">Unable to process request</p>
                  <p className="text-xs opacity-90">{message.error}</p>
                </div>
              ) : (
                message.content
              )}
            </div>

            {isAssistant && !message.loading && !message.error && (
              <div className="mt-2 flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className="text-xs hover:bg-slate-700/50 px-2 py-1"
                  aria-label="Copy message"
                  title="Copy message"
                >
                  {copied ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5 mr-1" />
                      Copy
                    </>
                  )}
                </Button>
              </div>
            )}
          </>
        )}

        <div className="text-xs opacity-60 mt-2">
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </div>
      </div>
    </div>
  )
}
