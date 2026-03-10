import { InputHTMLAttributes, forwardRef } from 'react'

export interface ToggleProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label?: string
  description?: string
  onChange?: (checked: boolean) => void
}

export const Toggle = forwardRef<HTMLInputElement, ToggleProps>(
  ({ label, description, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (onChange) {
        onChange(e.target.checked)
      }
    }

    return (
    <div className="flex items-center justify-between">
      <div>
        {label && (
          <p className="text-sm font-medium text-slate-300">{label}</p>
        )}
        {description && (
          <p className="text-xs text-slate-400 mt-1">{description}</p>
        )}
      </div>

      <div className="relative">
        <input
          ref={ref}
          type="checkbox"
          className="sr-only"
          onChange={handleChange}
          {...props}
        />
        <div className={`
          w-14 h-8 rounded-full transition-colors duration-200 cursor-pointer
          ${props.checked ? 'bg-primary-600' : 'bg-slate-700'}
          ${props.disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `} />
        <div className={`
          absolute top-1 left-1 w-6 h-6 rounded-full bg-white
          transition-transform duration-200 transform
          ${props.checked ? 'translate-x-6' : 'translate-x-0'}
        `} />
      </div>
    </div>
  )}
)

Toggle.displayName = 'Toggle'
