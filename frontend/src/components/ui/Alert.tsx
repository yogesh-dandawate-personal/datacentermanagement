import { ReactNode } from 'react'
import { AlertCircle, CheckCircle, AlertTriangle, InfoIcon, X } from 'lucide-react'

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  message: string
  icon?: ReactNode
  action?: ReactNode
  onClose?: () => void
  className?: string
}

const variantStyles = {
  info: {
    container: 'bg-info-500/10 border border-info-500/30 text-info-200',
    icon: 'text-info-400',
  },
  success: {
    container: 'bg-success-500/10 border border-success-500/30 text-success-200',
    icon: 'text-success-400',
  },
  warning: {
    container: 'bg-warning-500/10 border border-warning-500/30 text-warning-200',
    icon: 'text-warning-400',
  },
  error: {
    container: 'bg-danger-500/10 border border-danger-500/30 text-danger-200',
    icon: 'text-danger-400',
  },
}

const defaultIcons = {
  info: <InfoIcon className="w-5 h-5" />,
  success: <CheckCircle className="w-5 h-5" />,
  warning: <AlertTriangle className="w-5 h-5" />,
  error: <AlertCircle className="w-5 h-5" />,
}

export function Alert({
  variant = 'info',
  title,
  message,
  icon,
  action,
  onClose,
  className = '',
}: AlertProps) {
  const styles = variantStyles[variant]

  return (
    <div className={`
      rounded-lg p-4 flex items-start gap-3
      ${styles.container} ${className}
    `}>
      <div className={`flex-shrink-0 mt-0.5 ${styles.icon}`}>
        {icon || defaultIcons[variant]}
      </div>

      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="font-semibold text-sm mb-1">{title}</h4>
        )}
        <p className="text-sm opacity-90">{message}</p>
        {action && (
          <div className="mt-3">
            {action}
          </div>
        )}
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity"
          aria-label="Close alert"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  )
}
