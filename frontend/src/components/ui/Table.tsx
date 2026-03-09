import { ReactNode } from 'react'

export interface Column {
  key: string
  header: string
  render?: (value: any, row: any) => ReactNode
  width?: string
  sortable?: boolean
}

interface TableProps {
  columns: Column[]
  data: any[]
  striped?: boolean
  hover?: boolean
  loading?: boolean
  emptyMessage?: string
  className?: string
}

export function Table({
  columns,
  data,
  striped = true,
  hover = true,
  emptyMessage = 'No data available',
  className = '',
}: TableProps) {
  return (
    <div className={`overflow-x-auto rounded-lg border border-slate-700/30 ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-800/50 border-b border-slate-700/30">
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-6 py-4 text-left font-semibold text-slate-200 whitespace-nowrap"
                style={{ width: column.width }}
              >
                {column.header}
                {column.sortable && (
                  <span className="ml-2 opacity-50">↕</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-6 py-8 text-center text-slate-400"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`
                  border-b border-slate-700/30
                  ${striped && rowIndex % 2 === 0 ? 'bg-slate-800/20' : ''}
                  ${hover ? 'hover:bg-slate-800/30 transition-colors' : ''}
                `}
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className="px-6 py-4 text-slate-300"
                  >
                    {column.render
                      ? column.render(row[column.key], row)
                      : row[column.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
