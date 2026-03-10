import { InputHTMLAttributes, ReactNode, forwardRef } from 'react'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  icon?: ReactNode
  hint?: string
  required?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, hint, required, className = '', ...props }, ref) => (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-slate-300 mb-2">
          {label}
          {required && <span className="text-danger-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500">
            {icon}
          </div>
        )}

        <input
          ref={ref}
          className={`
            w-full rounded-lg font-medium transition duration-200
            text-white placeholder-slate-500
            ${icon ? 'pl-10 pr-4' : 'px-4'} py-2
            bg-slate-800/50 border border-slate-700/50
            focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20
            focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? 'border-danger-500/50 bg-danger-500/5' : ''}
            ${className}
          `}
          {...props}
        />
      </div>

      {error && (
        <p className="text-sm text-danger-400 mt-1">{error}</p>
      )}

      {hint && !error && (
        <p className="text-sm text-slate-400 mt-1">{hint}</p>
      )}
    </div>
  )
)

Input.displayName = 'Input'
