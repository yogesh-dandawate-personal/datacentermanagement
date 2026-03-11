/**
 * TradeHistory Component
 * Display and filter trade history
 */

import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownLeft, Download, Filter, Search, Clock, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input, Select, Badge, Table, Pagination, Dialog, Spinner } from '../ui'
import type { Trade, TradeStatus } from '../../types/marketplace'
import { useTrading } from '../../hooks/useTrading'

interface TradeHistoryProps {
  organizationId?: string
  maxItems?: number
}

export function TradeHistory({ organizationId, maxItems }: TradeHistoryProps) {
  const { trades, fetchTradeHistory, completeTrade } = useTrading(organizationId)

  const [filteredTrades, setFilteredTrades] = useState<Trade[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<TradeStatus | 'all'>('all')
  const [typeFilter, setTypeFilter] = useState<'buy' | 'sell' | 'all'>('all')
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [sortBy, setSortBy] = useState<'date_desc' | 'date_asc' | 'amount_desc' | 'amount_asc'>('date_desc')

  const itemsPerPage = maxItems || 25

  useEffect(() => {
    if (organizationId) {
      fetchTradeHistory('all')
    }
  }, [organizationId, fetchTradeHistory])

  useEffect(() => {
    let filtered = [...trades]

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (t) =>
          t.batch_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.counterparty?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.id.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((t) => t.status === statusFilter)
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter((t) => t.type === typeFilter)
    }

    // Date range filter
    if (dateRange !== 'all') {
      const now = new Date()
      const days = parseInt(dateRange)
      const cutoffDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
      filtered = filtered.filter((t) => new Date(t.trade_date) >= cutoffDate)
    }

    // Sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date_desc':
          return new Date(b.trade_date).getTime() - new Date(a.trade_date).getTime()
        case 'date_asc':
          return new Date(a.trade_date).getTime() - new Date(b.trade_date).getTime()
        case 'amount_desc':
          return b.total_price - a.total_price
        case 'amount_asc':
          return a.total_price - b.total_price
        default:
          return 0
      }
    })

    setFilteredTrades(filtered)
    setCurrentPage(1)
  }, [trades, searchTerm, statusFilter, typeFilter, dateRange, sortBy])

  const paginatedTrades = filteredTrades.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const totalPages = Math.ceil(filteredTrades.length / itemsPerPage)

  const handleExportCSV = () => {
    const csvContent = [
      ['Trade ID', 'Date', 'Type', 'Batch', 'Counterparty', 'Quantity', 'Price', 'Total', 'Status'].join(','),
      ...filteredTrades.map((trade) =>
        [
          trade.id,
          new Date(trade.trade_date).toLocaleDateString(),
          trade.type,
          trade.batch_name,
          trade.counterparty,
          trade.quantity,
          trade.price_per_credit.toFixed(2),
          trade.total_price.toFixed(2),
          trade.status,
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `trade-history-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  const getStatusBadge = (status: TradeStatus) => {
    switch (status) {
      case 'completed':
        return (
          <Badge className="bg-green-600/20 text-green-300 border-green-500/30 gap-1">
            <CheckCircle className="w-3 h-3" />
            Completed
          </Badge>
        )
      case 'pending':
        return (
          <Badge className="bg-amber-600/20 text-amber-300 border-amber-500/30 gap-1">
            <Clock className="w-3 h-3" />
            Pending
          </Badge>
        )
      case 'cancelled':
        return (
          <Badge className="bg-red-600/20 text-red-300 border-red-500/30 gap-1">
            <XCircle className="w-3 h-3" />
            Cancelled
          </Badge>
        )
      case 'failed':
        return (
          <Badge className="bg-red-600/20 text-red-300 border-red-500/30 gap-1">
            <XCircle className="w-3 h-3" />
            Failed
          </Badge>
        )
      default:
        return <Badge>{status}</Badge>
    }
  }

  if (!organizationId) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-slate-400">
          Organization ID required to view trade history
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white">Trade History</CardTitle>
            <CardDescription>View and manage your trading activity</CardDescription>
          </div>
          <Button variant="outline" onClick={handleExportCSV} className="gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Filters */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
              <Input
                type="text"
                placeholder="Search by batch, counterparty, or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </Button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as TradeStatus | 'all')}
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
              <option value="cancelled">Cancelled</option>
              <option value="failed">Failed</option>
            </Select>

            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as 'buy' | 'sell' | 'all')}
            >
              <option value="all">All Types</option>
              <option value="buy">Buys</option>
              <option value="sell">Sells</option>
            </Select>

            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
            >
              <option value="all">All Time</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </Select>

            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
            >
              <option value="date_desc">Newest First</option>
              <option value="date_asc">Oldest First</option>
              <option value="amount_desc">Highest Amount</option>
              <option value="amount_asc">Lowest Amount</option>
            </Select>
          </div>
        </div>

        {/* Results count */}
        <div className="text-sm text-slate-400">
          Showing {paginatedTrades.length} of {filteredTrades.length} trades
        </div>

        {/* Trade Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Date</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Type</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Batch</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Quantity</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Price</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Total</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Status</th>
                <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Action</th>
              </tr>
            </thead>
            <tbody>
              {paginatedTrades.length > 0 ? (
                paginatedTrades.map((trade) => (
                  <tr
                    key={trade.id}
                    className="border-b border-slate-700/50 hover:bg-slate-800/50 transition cursor-pointer"
                    onClick={() => {
                      setSelectedTrade(trade)
                      setIsDetailOpen(true)
                    }}
                  >
                    <td className="py-4 px-4 text-slate-300">
                      {new Date(trade.trade_date).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        {trade.type === 'buy' ? (
                          <>
                            <ArrowDownLeft className="w-4 h-4 text-green-400" />
                            <span className="text-green-400 font-medium">Buy</span>
                          </>
                        ) : (
                          <>
                            <ArrowUpRight className="w-4 h-4 text-blue-400" />
                            <span className="text-blue-400 font-medium">Sell</span>
                          </>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <div>
                        <p className="text-white font-medium">{trade.batch_name}</p>
                        <p className="text-xs text-slate-400">{trade.counterparty}</p>
                      </div>
                    </td>
                    <td className="text-right py-4 px-4 text-white font-semibold">
                      {trade.quantity.toLocaleString()}
                    </td>
                    <td className="text-right py-4 px-4 text-white">
                      ${trade.price_per_credit.toFixed(2)}
                    </td>
                    <td className="text-right py-4 px-4 text-white font-bold">
                      ${trade.total_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="text-center py-4 px-4">{getStatusBadge(trade.status)}</td>
                    <td className="text-center py-4 px-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedTrade(trade)
                          setIsDetailOpen(true)
                        }}
                      >
                        Details
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-slate-400">
                    No trades match your criteria
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        )}
      </CardContent>

      {/* Trade Detail Dialog */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        {selectedTrade && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <Card className="w-full max-w-2xl">
              <CardHeader>
                <CardTitle className="text-white">Trade Details</CardTitle>
                <CardDescription>ID: {selectedTrade.id}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Trade Date</p>
                    <p className="text-lg font-semibold text-white">
                      {new Date(selectedTrade.trade_date).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Type</p>
                    <p className={`text-lg font-semibold ${selectedTrade.type === 'buy' ? 'text-green-400' : 'text-blue-400'}`}>
                      {selectedTrade.type === 'buy' ? 'Purchase' : 'Sale'}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Quantity</p>
                    <p className="text-lg font-semibold text-white">
                      {selectedTrade.quantity.toLocaleString()} credits
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Price per Credit</p>
                    <p className="text-lg font-semibold text-white">
                      ${selectedTrade.price_per_credit.toFixed(2)}
                    </p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 col-span-2">
                    <p className="text-xs text-slate-400 mb-1">Total Amount</p>
                    <p className="text-2xl font-bold text-white">
                      ${selectedTrade.total_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-slate-400">Batch</p>
                    <p className="text-white font-medium">{selectedTrade.batch_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Counterparty</p>
                    <p className="text-white font-medium">{selectedTrade.counterparty}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">Status</p>
                    <div className="mt-1">{getStatusBadge(selectedTrade.status)}</div>
                  </div>
                  {selectedTrade.completion_date && (
                    <div>
                      <p className="text-xs text-slate-400">Completed On</p>
                      <p className="text-white font-medium">
                        {new Date(selectedTrade.completion_date).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setIsDetailOpen(false)}
                    className="flex-1"
                  >
                    Close
                  </Button>
                  {selectedTrade.status === 'pending' && (
                    <Button
                      onClick={async () => {
                        await completeTrade(selectedTrade.id)
                        setIsDetailOpen(false)
                      }}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    >
                      Complete Trade
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </Dialog>
    </Card>
  )
}
