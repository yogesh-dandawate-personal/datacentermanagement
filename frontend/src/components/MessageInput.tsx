/**
 * Message Input Component
 * Input field for copilot messages with send button
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import { Input } from './ui/Input'
import { Button } from './ui/Button'

interface MessageInputProps {
  onSend: (message: string) => void
  isLoading?: boolean
  placeholder?: string
  autoFocus?: boolean
}

export function MessageInput({
  onSend,
  isLoading = false,
  placeholder = 'Ask me anything about your energy data...',
  autoFocus = true
}: MessageInputProps) {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  // Load draft from localStorage on mount
  useEffect(() => {
    const draft = localStorage.getItem('copilot_draft')
    if (draft) {
      setValue(draft)
    }

    if (autoFocus && inputRef.current) {
      inputRef.current.focus()
    }
  }, [autoFocus])

  // Auto-save draft to localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      if (value.trim()) {
        localStorage.setItem('copilot_draft', value)
      } else {
        localStorage.removeItem('copilot_draft')
      }
    }, 500)

    return () => clearTimeout(timer)
  }, [value])

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()

    if (value.trim() && !isLoading) {
      onSend(value)
      setValue('')
      localStorage.removeItem('copilot_draft')

      // Re-focus input
      if (inputRef.current) {
        inputRef.current.focus()
      }
    }
  }, [value, isLoading, onSend])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Send on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e as any)
    }
  }, [handleSubmit])

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            ref={inputRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className="w-full"
            autoComplete="off"
            aria-label="Message input"
            title="Type your question here. Press Ctrl+Enter to send."
          />
          <div className="text-xs text-slate-500 mt-1">
            <span className="block sm:inline">Tip: Press </span>
            <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-xs font-mono">
              Ctrl
            </kbd>
            <span className="mx-1">+</span>
            <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-xs font-mono">
              Enter
            </kbd>
            <span> to send</span>
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          disabled={!value.trim() || isLoading}
          className="flex-shrink-0"
          aria-label="Send message"
          title="Send message"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </form>
  )
}
