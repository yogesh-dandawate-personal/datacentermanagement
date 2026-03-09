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
