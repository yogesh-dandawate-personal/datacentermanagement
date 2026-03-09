import { ChevronLeft, ChevronRight } from 'lucide-react'

interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  siblings?: number
  className?: string
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  siblings = 1,
  className = '',
}: PaginationProps) {
  const getPages = () => {
    const pages: (number | string)[] = []
    const leftSibling = Math.max(currentPage - siblings, 1)
    const rightSibling = Math.min(currentPage + siblings, totalPages)

    // Left ellipsis
    if (leftSibling > 1) {
      pages.push(1)
      if (leftSibling > 2) pages.push('...')
    }

    // Middle pages
    for (let i = leftSibling; i <= rightSibling; i++) {
      pages.push(i)
    }

    // Right ellipsis
    if (rightSibling < totalPages) {
      if (rightSibling < totalPages - 1) pages.push('...')
      pages.push(totalPages)
    }

    return pages
  }

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="p-2 rounded-lg border border-slate-700 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        aria-label="Previous page"
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      {getPages().map((page, index) => (
        <button
          key={index}
          onClick={() => typeof page === 'number' && onPageChange(page)}
          disabled={page === '...'}
          className={`
            min-w-[2.5rem] h-10 rounded-lg font-medium transition-colors
            ${page === currentPage
              ? 'bg-primary-600 text-white border border-primary-600'
              : page === '...'
                ? 'cursor-default border border-transparent'
                : 'border border-slate-700 text-slate-300 hover:bg-slate-800'
            }
          `}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="p-2 rounded-lg border border-slate-700 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        aria-label="Next page"
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  )
}
