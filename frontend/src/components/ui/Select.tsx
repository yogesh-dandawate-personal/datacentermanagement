import { SelectHTMLAttributes, ReactNode, forwardRef } from 'react'
import { ChevronDown } from 'lucide-react'

interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  hint?: string
  options: SelectOption[]
  placeholder?: string
  icon?: ReactNode
  required?: boolean
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, hint, options, placeholder, icon, required, className = '', ...props }, ref) => (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-slate-300 mb-2">
          {label}
          {required && <span className="text-danger-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500 pointer-events-none">
            {icon}
          </div>
        )}

        <select
          ref={ref}
          className={`
            w-full rounded-lg font-medium appearance-none transition duration-200
            text-white placeholder-slate-500 cursor-pointer
            ${icon ? 'pl-10 pr-10' : 'pl-4 pr-10'} py-2
            bg-slate-800/50 border border-slate-700/50
            focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20
            focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed
            ${error ? 'border-danger-500/50 bg-danger-500/5' : ''}
            ${className}
          `}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </option>
          ))}
        </select>

        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-500 pointer-events-none" />
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

Select.displayName = 'Select'
