import { ReactNode } from 'react'

interface BadgeProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'
  size?: 'sm' | 'md' | 'lg'
  icon?: ReactNode
  children: ReactNode
  className?: string
}

const variantStyles = {
  primary: 'bg-primary-500/20 text-primary-300 border border-primary-500/30',
  secondary: 'bg-secondary-500/20 text-secondary-300 border border-secondary-500/30',
  success: 'bg-success-500/20 text-success-300 border border-success-500/30',
  warning: 'bg-warning-500/20 text-warning-300 border border-warning-500/30',
  danger: 'bg-danger-500/20 text-danger-300 border border-danger-500/30',
  info: 'bg-info-500/20 text-info-300 border border-info-500/30',
}

const sizeStyles = {
  sm: 'px-2 py-1 text-xs rounded-md',
  md: 'px-3 py-1.5 text-sm rounded-lg',
  lg: 'px-4 py-2 text-base rounded-lg',
}

export function Badge({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  className = '',
}: BadgeProps) {
  return (
    <span className={`
      inline-flex items-center gap-1.5 font-medium transition-colors
      ${variantStyles[variant]} ${sizeStyles[size]} ${className}
    `}>
      {icon}
      {children}
    </span>
  )
}
