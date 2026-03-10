import { InputHTMLAttributes, forwardRef } from 'react'

export interface RadioProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  ({ label, error, className = '', ...props }, ref) => (
    <div className="flex items-start gap-3">
      <div className="relative flex items-center mt-1">
        <input
          ref={ref}
          type="radio"
          className="sr-only"
          {...props}
        />
        <div className={`
          w-5 h-5 rounded-full border-2 transition-colors duration-200
          flex items-center justify-center cursor-pointer
          ${props.checked
            ? 'bg-primary-600 border-primary-600'
            : 'border-slate-700/50 bg-slate-800/50 hover:border-slate-600'
          }
          ${props.disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}>
          {props.checked && (
            <div className="w-1.5 h-1.5 rounded-full bg-white" />
          )}
        </div>
      </div>

      {label && (
        <div className="flex-1">
          <label className="text-sm font-medium text-slate-300 cursor-pointer">
            {label}
          </label>
          {error && (
            <p className="text-xs text-danger-400 mt-1">{error}</p>
          )}
        </div>
      )}
    </div>
  )
)

Radio.displayName = 'Radio'
