import { ReactNode } from 'react'
import { ChevronRight } from 'lucide-react'

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: ReactNode
  active?: boolean
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[]
  onNavigate?: (href: string) => void
  className?: string
}

export function Breadcrumb({
  items,
  onNavigate,
  className = '',
}: BreadcrumbProps) {
  return (
    <nav
      className={`flex items-center gap-2 text-sm ${className}`}
      aria-label="Breadcrumb"
    >
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {item.href && onNavigate && !item.active ? (
            <button
              onClick={() => onNavigate(item.href!)}
              className="flex items-center gap-1.5 text-primary-400 hover:text-primary-300 transition-colors"
            >
              {item.icon && (
                <span className="w-4 h-4">{item.icon}</span>
              )}
              {item.label}
            </button>
          ) : (
            <span className={`flex items-center gap-1.5 ${
              item.active ? 'text-white font-medium' : 'text-slate-400'
            }`}>
              {item.icon && (
                <span className="w-4 h-4">{item.icon}</span>
              )}
              {item.label}
            </span>
          )}

          {index < items.length - 1 && (
            <ChevronRight className="w-4 h-4 text-slate-600" />
          )}
        </div>
      ))}
    </nav>
  )
}
