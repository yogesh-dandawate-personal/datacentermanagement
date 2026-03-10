/**
 * ForecastChart Component
 * 6-month emissions forecast with confidence intervals
 */

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, AlertCircle } from 'lucide-react'
import type { ForecastData } from '../services/api'

interface ForecastChartProps {
  forecast: ForecastData
}

export function ForecastChart({ forecast }: ForecastChartProps) {
  if (!forecast || !forecast.projections || forecast.projections.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-slate-500">
        <AlertCircle className="w-5 h-5 mr-2" />
        No forecast data available
      </div>
    )
  }

  // Format data for chart
  const chartData = forecast.projections.map((proj) => ({
    month: new Date(proj.month).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    emissions: proj.emissions_co2,
    upperBound: proj.confidence_upper,
    lowerBound: proj.confidence_lower,
  }))

  // Calculate trend
  const firstMonth = forecast.projections[0]?.emissions_co2 || 0
  const lastMonth = forecast.projections[forecast.projections.length - 1]?.emissions_co2 || 0
  const trend = lastMonth > firstMonth ? 'increasing' : 'decreasing'
  const trendPercent = Math.abs(((lastMonth - firstMonth) / firstMonth) * 100).toFixed(1)

  return (
    <div className="space-y-4">
      {/* Forecast Summary */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Model Accuracy</p>
          <p className="text-3xl font-bold text-cyan-400 mt-1">
            {forecast.accuracy_percentage}%
          </p>
          <p className="text-xs text-slate-500 mt-1">based on historical data</p>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Projected Trend</p>
          <p
            className={`text-3xl font-bold mt-1 ${
              trend === 'decreasing' ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {trend === 'decreasing' ? '↓' : '↑'} {trendPercent}%
          </p>
          <p className="text-xs text-slate-500 mt-1 capitalize">{trend} emissions</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <defs>
            <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="emissionsForecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />

          <XAxis
            dataKey="month"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#94a3b8' }}
          />

          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Emissions (tCO₂e)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '12px',
            }}
            labelStyle={{ color: '#f1f5f9', fontWeight: 'bold', marginBottom: '8px' }}
            itemStyle={{ color: '#cbd5e1', fontSize: '13px' }}
            formatter={(value: number) => value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
            formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: '13px' }}>{value}</span>}
          />

          {/* Confidence Interval Area */}
          <Area
            type="monotone"
            dataKey="upperBound"
            stroke="none"
            fill="url(#confidenceGradient)"
            name="Upper Bound"
          />

          <Area
            type="monotone"
            dataKey="lowerBound"
            stroke="none"
            fill="url(#confidenceGradient)"
            name="Lower Bound"
          />

          {/* Forecast Line */}
          <Area
            type="monotone"
            dataKey="emissions"
            stroke="#3b82f6"
            strokeWidth={3}
            fill="url(#emissionsForecastGradient)"
            name="Forecast"
            strokeDasharray="5 5"
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Info */}
      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <TrendingUp className="w-4 h-4 text-blue-400 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-blue-200 font-medium">Forecast Insight</p>
            <p className="text-xs text-slate-400 mt-1">
              Based on {forecast.accuracy_percentage}% accuracy, emissions are projected to{' '}
              {trend === 'decreasing' ? 'decrease' : 'increase'} by {trendPercent}% over the next 6
              months. Confidence intervals show the range of possible outcomes.
            </p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 border-t-2 border-dashed border-blue-500"></div>
          <span>Forecast Projection</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-cyan-400/20 border border-cyan-400/50 rounded"></div>
          <span>Confidence Interval</span>
        </div>
      </div>
    </div>
  )
}
