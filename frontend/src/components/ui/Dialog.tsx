import { ReactNode, useEffect } from 'react'
import { X } from 'lucide-react'

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  description?: string
  children: ReactNode
  footer?: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeStyles = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
}

export function Dialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  footer,
  size = 'md',
  className = '',
}: DialogProps) {
  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) {
        onOpenChange(false)
      }
    }

    if (open) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'unset'
    }
  }, [open, onOpenChange])

  if (!open) return null

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className={`
            relative w-full rounded-2xl
            bg-gradient-to-br from-slate-900 to-slate-950
            backdrop-blur-xl border border-slate-700/50
            shadow-2xl
            ${sizeStyles[size]}
            ${className}
          `}
          role="dialog"
          aria-modal="true"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          {title && (
            <div className="border-b border-slate-700/30 px-6 py-4 flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">{title}</h2>
                {description && (
                  <p className="text-sm text-slate-400 mt-1">{description}</p>
                )}
              </div>
              <button
                onClick={() => onOpenChange(false)}
                className="p-1 hover:bg-slate-800 rounded-lg transition-colors"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5 text-slate-400 hover:text-white" />
              </button>
            </div>
          )}

          {/* Content */}
          <div className="p-6">
            {children}
          </div>

          {/* Footer */}
          {footer && (
            <div className="border-t border-slate-700/30 px-6 py-4 flex items-center justify-end gap-3">
              {footer}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
