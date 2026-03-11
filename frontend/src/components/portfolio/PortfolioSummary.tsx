/**
 * PortfolioSummary Component
 * Display portfolio overview with key metrics
 */

import { TrendingUp, TrendingDown, Wallet, Target, Activity, DollarSign } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Badge } from '../ui'
import type { PortfolioSummary as PortfolioSummaryType } from '../../types/marketplace'

interface PortfolioSummaryProps {
  summary: PortfolioSummaryType | null
  isLoading?: boolean
}

export function PortfolioSummary({ summary, isLoading }: PortfolioSummaryProps) {
  if (isLoading || !summary) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="pt-6">
              <div className="h-20 bg-slate-800/50 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  const isPositive = summary.monthly_change_percent >= 0
  const avgCostBasis = summary.total_credits > 0 ? summary.total_value / summary.total_credits : 0

  return (
    <div className="space-y-6">
      {/* Main Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Credits */}
        <Card className="bg-gradient-to-br from-green-600/20 to-green-700/20 border-green-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Credits</p>
                <p className="text-3xl font-bold text-white mb-1">
                  {summary.total_credits.toLocaleString()}
                </p>
                <div className="flex items-center gap-1">
                  <Badge className="bg-green-600/30 text-green-300 border-green-500/50 text-xs">
                    {summary.active_batches} active batches
                  </Badge>
                </div>
              </div>
              <Wallet className="w-10 h-10 text-green-400" />
            </div>
          </CardContent>
        </Card>

        {/* Total Value */}
        <Card className="bg-gradient-to-br from-blue-600/20 to-blue-700/20 border-blue-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Portfolio Value</p>
                <p className="text-3xl font-bold text-white mb-1">
                  ${summary.total_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
                <div className="flex items-center gap-1">
                  {isPositive ? (
                    <TrendingUp className="w-3 h-3 text-green-400" />
                  ) : (
                    <TrendingDown className="w-3 h-3 text-red-400" />
                  )}
                  <span className={`text-xs ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}{summary.monthly_change_percent.toFixed(1)}% this month
                  </span>
                </div>
              </div>
              <DollarSign className="w-10 h-10 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        {/* Average Quality */}
        <Card className="bg-gradient-to-br from-cyan-600/20 to-cyan-700/20 border-cyan-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Avg Quality Score</p>
                <p className="text-3xl font-bold text-white mb-1">
                  {summary.avg_quality_score.toFixed(1)}%
                </p>
                <div className="flex items-center gap-1">
                  <Badge
                    className={
                      summary.avg_quality_score >= 90
                        ? 'bg-green-600/30 text-green-300 border-green-500/50'
                        : summary.avg_quality_score >= 75
                        ? 'bg-blue-600/30 text-blue-300 border-blue-500/50'
                        : 'bg-amber-600/30 text-amber-300 border-amber-500/50'
                    }
                  >
                    {summary.avg_quality_score >= 90
                      ? 'Excellent'
                      : summary.avg_quality_score >= 75
                      ? 'Good'
                      : 'Fair'}
                  </Badge>
                </div>
              </div>
              <Target className="w-10 h-10 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        {/* Cost Basis */}
        <Card className="bg-gradient-to-br from-purple-600/20 to-purple-700/20 border-purple-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Avg Cost Basis</p>
                <p className="text-3xl font-bold text-white mb-1">
                  ${avgCostBasis.toFixed(2)}
                </p>
                <div className="flex items-center gap-1">
                  <Activity className="w-3 h-3 text-purple-400" />
                  <span className="text-xs text-purple-300">per credit</span>
                </div>
              </div>
              <Activity className="w-10 h-10 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white">Portfolio Breakdown</CardTitle>
          <CardDescription>Detailed analysis of your carbon credit holdings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center gap-2 mb-2">
                <Wallet className="w-4 h-4 text-green-400" />
                <p className="text-xs text-slate-400">Active Credits</p>
              </div>
              <p className="text-2xl font-bold text-white">
                {(summary.total_credits - summary.retired_credits - summary.traded_credits).toLocaleString()}
              </p>
              <p className="text-xs text-slate-500 mt-1">Available for trading</p>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-4 h-4 text-blue-400" />
                <p className="text-xs text-slate-400">Traded Credits</p>
              </div>
              <p className="text-2xl font-bold text-white">{summary.traded_credits.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">
                {((summary.traded_credits / summary.total_credits) * 100).toFixed(1)}% of total
              </p>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center gap-2 mb-2">
                <Target className="w-4 h-4 text-purple-400" />
                <p className="text-xs text-slate-400">Retired Credits</p>
              </div>
              <p className="text-2xl font-bold text-white">{summary.retired_credits.toLocaleString()}</p>
              <p className="text-xs text-slate-500 mt-1">
                {((summary.retired_credits / summary.total_credits) * 100).toFixed(1)}% of total
              </p>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <p className="text-xs text-slate-400">Active Batches</p>
              </div>
              <p className="text-2xl font-bold text-white">{summary.active_batches}</p>
              <p className="text-xs text-slate-500 mt-1">Unique credit batches</p>
            </div>
          </div>

          {/* Performance Badge */}
          <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-white mb-1">Monthly Performance</h4>
                <p className="text-sm text-slate-400">
                  Your portfolio {isPositive ? 'gained' : 'lost'}{' '}
                  <span className={`font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}
                    {summary.monthly_change_percent.toFixed(2)}%
                  </span>{' '}
                  in value this month
                </p>
              </div>
              <Badge
                className={
                  isPositive
                    ? 'bg-green-600/20 text-green-300 border-green-500/30'
                    : 'bg-red-600/20 text-red-300 border-red-500/30'
                }
              >
                {isPositive ? 'Up' : 'Down'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
