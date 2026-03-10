import { ArrowUpRight, ArrowDownLeft, Clock, CheckCircle, XCircle, Zap, TrendingUp } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from '../components/ui'
import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface Trade {
  id: string
  type: 'buy' | 'sell'
  batchName: string
  counterparty: string
  quantity: number
  pricePerCredit: number
  totalValue: number
  status: 'pending' | 'completed' | 'cancelled'
  date: string
  completionDate?: string
}

interface TradeStats {
  totalTradeCount: number
  totalVolume: number
  totalSpent: number
  totalEarned: number
}

const mockTrades: Trade[] = [
  {
    id: 'trade_001',
    type: 'buy',
    batchName: 'Data Center Efficiency Credits Q1 2026',
    counterparty: 'GreenTech Industries',
    quantity: 250,
    pricePerCredit: 35.50,
    totalValue: 8875.00,
    status: 'completed',
    date: '2026-03-05',
    completionDate: '2026-03-05',
  },
  {
    id: 'trade_002',
    type: 'sell',
    batchName: 'Energy Optimization Credits 2025',
    counterparty: 'Sustainable Solutions Inc',
    quantity: 500,
    pricePerCredit: 38.00,
    totalValue: 19000.00,
    status: 'completed',
    date: '2026-03-02',
    completionDate: '2026-03-02',
  },
  {
    id: 'trade_003',
    type: 'buy',
    batchName: 'Renewable Energy Integration Batch',
    counterparty: 'Carbon Neutral Corp',
    quantity: 100,
    pricePerCredit: 42.00,
    totalValue: 4200.00,
    status: 'pending',
    date: '2026-03-08',
  },
  {
    id: 'trade_004',
    type: 'sell',
    batchName: 'Verified Carbon Offsets',
    counterparty: 'EcoBalance Ltd',
    quantity: 300,
    pricePerCredit: 39.99,
    totalValue: 11997.00,
    status: 'completed',
    date: '2026-02-28',
    completionDate: '2026-02-28',
  },
  {
    id: 'trade_005',
    type: 'buy',
    batchName: 'Energy Efficiency Improvements Q1 2026',
    counterparty: 'ClimateAction Partners',
    quantity: 150,
    pricePerCredit: 36.50,
    totalValue: 5475.00,
    status: 'cancelled',
    date: '2026-02-25',
  },
]

const mockMonthlyVolume = [
  { month: 'January', buys: 5000, sells: 3200 },
  { month: 'February', buys: 7500, sells: 6800 },
  { month: 'March', buys: 12500, sells: 19000 },
]

const mockTradeDistribution = [
  { name: 'Completed', value: 3, fill: '#10b981' },
  { name: 'Pending', value: 1, fill: '#f59e0b' },
  { name: 'Cancelled', value: 1, fill: '#ef4444' },
]

export function Trading() {
  const [trades] = useState<Trade[]>(mockTrades)

  // Calculate statistics
  const completedTrades = trades.filter(t => t.status === 'completed')
  const buyTrades = completedTrades.filter(t => t.type === 'buy')
  const sellTrades = completedTrades.filter(t => t.type === 'sell')

  const stats: TradeStats = {
    totalTradeCount: trades.length,
    totalVolume: trades.reduce((sum, t) => sum + t.quantity, 0),
    totalSpent: buyTrades.reduce((sum, t) => sum + t.totalValue, 0),
    totalEarned: sellTrades.reduce((sum, t) => sum + t.totalValue, 0),
  }

  const netPosition = stats.totalEarned - stats.totalSpent

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Trading Dashboard</h1>
        <p className="text-slate-400">Monitor your carbon credit trading activity and history</p>
      </section>

      {/* Trade Summary Stats */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-600/20 to-blue-700/20 border-blue-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Trades</p>
                <p className="text-2xl font-bold text-white">{stats.totalTradeCount}</p>
                <p className="text-xs text-slate-400 mt-1">
                  <span className="text-green-400">{completedTrades.length}</span> completed
                </p>
              </div>
              <Zap className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-600/20 to-green-700/20 border-green-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Bought</p>
                <p className="text-2xl font-bold text-white">${stats.totalSpent.toFixed(0)}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {buyTrades.length} purchases
                </p>
              </div>
              <ArrowDownLeft className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-cyan-600/20 to-cyan-700/20 border-cyan-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Sold</p>
                <p className="text-2xl font-bold text-white">${stats.totalEarned.toFixed(0)}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {sellTrades.length} sales
                </p>
              </div>
              <ArrowUpRight className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className={`bg-gradient-to-br ${netPosition >= 0 ? 'from-purple-600/20 to-purple-700/20 border-purple-500/30' : 'from-red-600/20 to-red-700/20 border-red-500/30'}`}>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Net Position</p>
                <p className={`text-2xl font-bold ${netPosition >= 0 ? 'text-white' : 'text-red-400'}`}>
                  ${Math.abs(netPosition).toFixed(0)}
                </p>
                <p className={`text-xs mt-1 ${netPosition >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {netPosition >= 0 ? 'Profit' : 'Loss'}
                </p>
              </div>
              <TrendingUp className={`w-8 h-8 ${netPosition >= 0 ? 'text-purple-400' : 'text-red-400'}`} />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Charts */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Trading Volume (Monthly)</CardTitle>
            <CardDescription>Buys vs sells over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={mockMonthlyVolume}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#e2e8f0' }}
                  formatter={(value) => `$${value}`}
                />
                <Legend />
                <Bar dataKey="buys" fill="#10b981" name="Purchases" />
                <Bar dataKey="sells" fill="#f59e0b" name="Sales" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-white">Trade Status Distribution</CardTitle>
            <CardDescription>Breakdown of all trades by status</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={mockTradeDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name} (${value})`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {mockTradeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </section>

      {/* Trade History */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Trade History</CardTitle>
            <CardDescription>Recent and ongoing trades</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {trades.map((trade) => (
                <div
                  key={trade.id}
                  className="border border-slate-700 rounded-lg p-4 hover:bg-slate-800/50 transition"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-4 flex-1">
                      <div className={`mt-1 ${trade.type === 'buy' ? 'text-green-400' : 'text-blue-400'}`}>
                        {trade.type === 'buy' ? (
                          <ArrowDownLeft className="w-5 h-5" />
                        ) : (
                          <ArrowUpRight className="w-5 h-5" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-white">{trade.batchName}</h3>
                        <p className="text-sm text-slate-400">
                          {trade.type === 'buy' ? 'Purchased from' : 'Sold to'} {trade.counterparty}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-white">${trade.totalValue.toFixed(2)}</p>
                      <p className="text-sm text-slate-400">{trade.quantity} credits @ ${trade.pricePerCredit.toFixed(2)}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-sm text-slate-400">
                      {trade.completionDate ? (
                        <span>Completed on {trade.completionDate}</span>
                      ) : (
                        <span>Initiated on {trade.date}</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {trade.status === 'completed' && (
                        <Badge className="bg-green-600/20 text-green-300 border-green-500/30 gap-1">
                          <CheckCircle className="w-3 h-3" />
                          Completed
                        </Badge>
                      )}
                      {trade.status === 'pending' && (
                        <Badge className="bg-amber-600/20 text-amber-300 border-amber-500/30 gap-1">
                          <Clock className="w-3 h-3" />
                          Pending
                        </Badge>
                      )}
                      {trade.status === 'cancelled' && (
                        <Badge className="bg-red-600/20 text-red-300 border-red-500/30 gap-1">
                          <XCircle className="w-3 h-3" />
                          Cancelled
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Recent Activity */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Trade Summary</CardTitle>
            <CardDescription>Year-to-date performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Buy Transactions</p>
                <p className="text-2xl font-bold text-green-400">{buyTrades.length}</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Sell Transactions</p>
                <p className="text-2xl font-bold text-blue-400">{sellTrades.length}</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Avg Buy Price</p>
                <p className="text-2xl font-bold text-white">
                  ${buyTrades.length > 0 ? (buyTrades.reduce((sum, t) => sum + t.pricePerCredit, 0) / buyTrades.length).toFixed(2) : '0.00'}
                </p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <p className="text-xs text-slate-400 mb-1">Avg Sell Price</p>
                <p className="text-2xl font-bold text-white">
                  ${sellTrades.length > 0 ? (sellTrades.reduce((sum, t) => sum + t.pricePerCredit, 0) / sellTrades.length).toFixed(2) : '0.00'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
