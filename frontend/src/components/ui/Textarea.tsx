import { TextareaHTMLAttributes, forwardRef } from 'react'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  hint?: string
  maxLength?: number
  showCharCount?: boolean
  required?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, hint, maxLength, showCharCount, required, className = '', value = '', onChange, ...props }, ref) => {
    const charCount = String(value).length

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-slate-300 mb-2">
            {label}
            {required && <span className="text-danger-500 ml-1">*</span>}
          </label>
        )}

        <textarea
          ref={ref}
          value={value}
          onChange={onChange}
          maxLength={maxLength}
          className={`
            w-full px-4 py-2 rounded-lg font-medium transition duration-200
            text-white placeholder-slate-500 resize-none
            bg-slate-800/50 border border-slate-700/50
            focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20
            focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? 'border-danger-500/50 bg-danger-500/5' : ''}
            ${className}
          `}
          {...props}
        />

        <div className="flex items-center justify-between mt-2">
          <div>
            {error && (
              <p className="text-sm text-danger-400">{error}</p>
            )}
            {hint && !error && (
              <p className="text-sm text-slate-400">{hint}</p>
            )}
          </div>

          {showCharCount && maxLength && (
            <p className="text-xs text-slate-400">
              {charCount} / {maxLength}
            </p>
          )}
        </div>
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
