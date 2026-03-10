/**
 * Comment Thread Component
 * Displays and manages comments on approval requests
 */

import { useState } from 'react'
import { Button, Textarea } from './ui'
import { ApprovalComment } from '../types/approval'
import { MessageSquare, Send } from 'lucide-react'

interface CommentThreadProps {
  comments: ApprovalComment[]
  onAddComment: (text: string) => void
  isLoading?: boolean
  isReadOnly?: boolean
}

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}

export function CommentThread({
  comments,
  onAddComment,
  isLoading = false,
  isReadOnly = false,
}: CommentThreadProps) {
  const [newComment, setNewComment] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!newComment.trim()) return

    setIsSubmitting(true)
    try {
      await onAddComment(newComment)
      setNewComment('')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-slate-400" />
        <h3 className="font-semibold text-white">
          Comments ({comments.length})
        </h3>
      </div>

      {/* Comments List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {comments.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No comments yet</p>
          </div>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className="flex gap-3 p-3 rounded-lg bg-slate-800/30 border border-slate-700/20"
            >
              {/* Avatar */}
              {comment.avatar ? (
                <img
                  src={comment.avatar}
                  alt={comment.author}
                  className="w-8 h-8 md:w-10 md:h-10 rounded-full flex-shrink-0"
                />
              ) : (
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 text-xs font-semibold text-white">
                  {comment.author.charAt(0)}
                </div>
              )}

              {/* Comment Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-2 flex-wrap">
                  <span className="font-medium text-white text-sm md:text-base">
                    {comment.author}
                  </span>
                  <span className="text-xs text-slate-500">
                    {formatTime(comment.timestamp)}
                  </span>
                  {comment.edited && (
                    <span className="text-xs text-slate-500 italic">
                      (edited)
                    </span>
                  )}
                </div>
                <p className="text-slate-300 text-sm mt-1 break-words">
                  {comment.text}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Comment Section */}
      {!isReadOnly && (
        <div className="border-t border-slate-700/30 pt-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Add a Comment
          </label>
          <div className="space-y-2">
            <Textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Share your feedback or request changes..."
              disabled={isSubmitting || isLoading}
              className="min-h-24"
            />
            <div className="flex justify-end">
              <Button
                onClick={handleSubmit}
                disabled={!newComment.trim() || isSubmitting || isLoading}
                loading={isSubmitting}
                size="sm"
              >
                <Send className="w-4 h-4 mr-1" />
                Post Comment
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
