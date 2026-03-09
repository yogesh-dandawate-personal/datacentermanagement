interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circle' | 'rect'
}

export function Skeleton({ className = '', variant = 'text' }: SkeletonProps) {
  const baseStyles = 'bg-slate-800 animate-pulse'

  const variantStyles = {
    text: 'h-4 rounded',
    circle: 'w-12 h-12 rounded-full',
    rect: 'h-32 rounded-lg',
  }

  return (
    <div className={`${baseStyles} ${variantStyles[variant]} ${className}`} />
  )
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton variant="text" className="w-3/4" />
          <Skeleton variant="text" className="w-1/2" />
        </div>
      ))}
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6">
      <Skeleton variant="text" className="mb-4 w-1/3" />
      <SkeletonList count={3} />
    </div>
  )
}

export function SkeletonStat() {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 space-y-4">
      <div className="flex justify-between items-start">
        <Skeleton variant="text" className="w-32" />
        <Skeleton variant="circle" />
      </div>
      <Skeleton variant="text" className="h-8 w-24" />
      <Skeleton variant="text" className="w-32" />
    </div>
  )
}

export function SkeletonChart({ height = 300 }: { height?: number }) {
  return (
    <div className="w-full animate-pulse" style={{ height: `${height}px` }}>
      <div className="h-full bg-slate-800/50 rounded flex items-end justify-around p-8 gap-4">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="flex-1 bg-slate-700/50 rounded-t" style={{ height: `${Math.random() * 100 + 20}%` }} />
        ))}
      </div>
    </div>
  )
}

export function SkeletonTable({ rows = 5, cols = 5 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 p-4 bg-slate-800/20 rounded">
          {Array.from({ length: cols }).map((_, colIndex) => (
            <div key={colIndex} className="h-4 bg-slate-700/50 rounded flex-1 animate-pulse" />
          ))}
        </div>
      ))}
    </div>
  )
}
