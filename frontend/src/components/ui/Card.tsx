import { HTMLAttributes } from 'react'

interface CardProps extends HTMLAttributes<HTMLDivElement> {}

export function Card({ className = '', ...props }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl ${className}`}
      {...props}
    />
  )
}

export function CardHeader({ className = '', ...props }: CardProps) {
  return <div className={`border-b border-slate-700/30 p-6 ${className}`} {...props} />
}

export function CardTitle({ className = '', ...props }: CardProps) {
  return <h3 className={`text-lg font-bold text-white ${className}`} {...props} />
}

export function CardDescription({ className = '', ...props }: CardProps) {
  return <p className={`text-sm text-slate-400 mt-1 ${className}`} {...props} />
}

export function CardContent({ className = '', ...props }: CardProps) {
  return <div className={`p-6 ${className}`} {...props} />
}

export function CardFooter({ className = '', ...props }: CardProps) {
  return (
    <div className={`border-t border-slate-700/30 px-6 py-4 flex items-center justify-between ${className}`} {...props} />
  )
}
