/**
 * Copilot Page
 * Main page for the AI copilot assistant with chat interface and history
 */

import { useState } from 'react'
import { ChevronLeft, ChevronRight, X, MessageSquare, Trash2 } from 'lucide-react'
import { CopilotChat } from '../components/CopilotChat'
import { useCopilot } from '../hooks/useCopilot'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export function Copilot() {
  const {
    messages,
    isLoading,
    error,
    conversations,
    currentConversationId,
    sendMessage,
    clearChat,
    deleteConversation,
    loadConversation,
    exportConversation
  } = useCopilot()

  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  // Filter conversations based on search
  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleNewConversation = () => {
    clearChat()
  }

  const handleDeleteConversation = (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(id)
    }
  }

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar - Conversation History */}
      <aside
        className={`
          fixed sm:relative left-0 top-0 h-screen
          bg-gradient-to-b from-slate-900 to-slate-950 border-r border-slate-800/50
          transition-all duration-300 z-40 flex flex-col
          ${sidebarOpen ? 'w-full sm:w-80' : 'w-0 sm:w-20'}
        `}
      >
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/50 flex-shrink-0">
          {sidebarOpen && (
            <div>
              <h3 className="font-semibold text-white text-sm">History</h3>
              <p className="text-xs text-slate-400">Previous conversations</p>
            </div>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden sm:inline-flex"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>

          {sidebarOpen && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
              className="sm:hidden"
              aria-label="Close sidebar"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {sidebarOpen && (
          <>
            {/* New Chat Button */}
            <div className="p-4 border-b border-slate-800/50">
              <Button
                variant="primary"
                fullWidth
                onClick={handleNewConversation}
                className="text-sm"
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                New Chat
              </Button>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-slate-800/50">
              <Input
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="text-sm"
                icon={null}
              />
            </div>

            {/* Conversations List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {filteredConversations.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-8">
                  {conversations.length === 0
                    ? 'No conversations yet. Start a new chat!'
                    : 'No matching conversations'}
                </p>
              ) : (
                filteredConversations.map(conversation => (
                  <button
                    key={conversation.id}
                    onClick={() => {
                      loadConversation(conversation.id)
                      // Close sidebar on mobile when selecting conversation
                      if (window.innerWidth < 640) {
                        setSidebarOpen(false)
                      }
                    }}
                    className={`
                      w-full text-left px-3 py-2 rounded-lg transition-all group
                      focus:outline-none focus:ring-2 focus:ring-primary-500/50
                      ${currentConversationId === conversation.id
                        ? 'bg-primary-600/20 border border-primary-500/50'
                        : 'hover:bg-slate-800/50 border border-transparent'
                      }
                    `}
                    aria-current={currentConversationId === conversation.id ? 'page' : undefined}
                  >
                    <div className="flex items-start gap-2 justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-200 truncate">
                          {conversation.title}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {conversation.messages.length} messages •{' '}
                          {new Date(conversation.updatedAt).toLocaleDateString()}
                        </p>
                      </div>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleDeleteConversation(e, conversation.id)}
                        className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label="Delete conversation"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5 text-red-400" />
                      </Button>
                    </div>
                  </button>
                ))
              )}
            </div>

            {/* Clear All Button */}
            {conversations.length > 0 && (
              <div className="p-4 border-t border-slate-800/50">
                <Button
                  variant="outline"
                  size="sm"
                  fullWidth
                  onClick={() => {
                    if (window.confirm('Delete all conversations? This cannot be undone.')) {
                      conversations.forEach(conv => deleteConversation(conv.id))
                    }
                  }}
                  className="text-xs"
                >
                  <Trash2 className="w-3.5 h-3.5 mr-2" />
                  Clear All
                </Button>
              </div>
            )}
          </>
        )}
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Mobile Close Sidebar Button */}
        {sidebarOpen && (
          <div className="h-16 flex items-center px-4 bg-slate-900 border-b border-slate-800/50 sm:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
              className="flex-shrink-0"
              aria-label="Close sidebar"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        )}

        {/* Chat Interface */}
        <CopilotChat
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSendMessage={sendMessage}
          onClearChat={handleNewConversation}
          onExport={exportConversation}
        />
      </div>
    </div>
  )
}
