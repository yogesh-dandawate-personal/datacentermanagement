import { ButtonHTMLAttributes, forwardRef, ReactNode } from 'react'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  fullWidth?: boolean
  icon?: ReactNode
}

const variants = {
  primary: 'bg-primary-600 hover:bg-primary-700 text-white disabled:opacity-50',
  secondary: 'bg-secondary-600 hover:bg-secondary-700 text-white disabled:opacity-50',
  outline: 'border border-slate-700 hover:bg-slate-800 text-white disabled:opacity-50',
  ghost: 'hover:bg-slate-800 text-slate-300 hover:text-white disabled:opacity-50',
  danger: 'bg-danger-600 hover:bg-danger-700 text-white disabled:opacity-50',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm rounded-md',
  md: 'px-4 py-2 text-base rounded-lg',
  lg: 'px-6 py-3 text-lg rounded-lg',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading = false, fullWidth = false, icon, className = '', children, ...props }, ref) => (
    <button
      ref={ref}
      disabled={loading || props.disabled}
      className={`
        font-medium transition-all duration-200
        focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-900
        focus:outline-none
        flex items-center justify-center gap-2
        ${variants[variant]} ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${loading ? 'opacity-75 cursor-not-allowed' : ''}
        ${className}
      `}
      {...props}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </button>
  )
)

Button.displayName = 'Button'
