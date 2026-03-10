/**
 * EmissionsTrendChart Component
 * 12-month emissions trend visualization with forecast overlay
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts'
import type { AnalyticsTrend } from '../services/api'

interface EmissionsTrendChartProps {
  trends: AnalyticsTrend[]
}

export function EmissionsTrendChart({ trends }: EmissionsTrendChartProps) {
  if (!trends || trends.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-slate-500">
        No emissions trend data available
      </div>
    )
  }

  // Format data for chart
  const chartData = trends.map((trend) => ({
    month: new Date(trend.month).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    emissions: trend.emissions_co2,
    energy: trend.energy_usage_kwh / 1000, // Convert to MWh
    renewable: trend.renewable_percentage,
    cost: trend.cost_usd / 1000, // Convert to thousands
    isForecast: trend.forecast || false,
  }))

  // Calculate trends
  const avgEmissions = trends.reduce((sum, t) => sum + t.emissions_co2, 0) / trends.length
  const latestEmissions = trends[trends.length - 1]?.emissions_co2 || 0
  const trend = latestEmissions > avgEmissions ? 'increasing' : 'decreasing'
  const trendPercent = Math.abs(((latestEmissions - avgEmissions) / avgEmissions) * 100).toFixed(1)

  return (
    <div className="space-y-4">
      {/* Metrics Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Current</p>
          <p className="text-2xl font-bold text-white mt-1">
            {latestEmissions.toLocaleString()}
          </p>
          <p className="text-xs text-slate-500 mt-1">tCO₂e</p>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Average</p>
          <p className="text-2xl font-bold text-white mt-1">
            {avgEmissions.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <p className="text-xs text-slate-500 mt-1">tCO₂e</p>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Trend</p>
          <p className={`text-2xl font-bold mt-1 ${trend === 'decreasing' ? 'text-green-400' : 'text-red-400'}`}>
            {trend === 'decreasing' ? '↓' : '↑'} {trendPercent}%
          </p>
          <p className="text-xs text-slate-500 mt-1 capitalize">{trend}</p>
        </div>

        <div className="bg-slate-800/30 rounded-lg p-4">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Renewable</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">
            {trends[trends.length - 1]?.renewable_percentage || 0}%
          </p>
          <p className="text-xs text-slate-500 mt-1">of total energy</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={350}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <defs>
            <linearGradient id="emissionsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
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
            yAxisId="left"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Emissions (tCO₂e)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
          />

          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Energy (MWh)', angle: 90, position: 'insideRight', fill: '#94a3b8' }}
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
          />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
            formatter={(value) => <span style={{ color: '#cbd5e1' }}>{value}</span>}
          />

          {/* Emissions Area + Line */}
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="emissions"
            stroke="#3b82f6"
            strokeWidth={3}
            fill="url(#emissionsGradient)"
            name="Emissions (tCO₂e)"
            strokeDasharray={(entry: any) => (entry.isForecast ? '5 5' : '0')}
          />

          {/* Energy Line */}
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="energy"
            stroke="#22d3ee"
            strokeWidth={2}
            dot={{ fill: '#22d3ee', r: 4 }}
            activeDot={{ r: 6 }}
            name="Energy (MWh)"
          />

          {/* Renewable Percentage (hidden, but available in tooltip) */}
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="renewable"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Renewable %"
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Legend Info */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span>Emissions Trend</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
          <span>Energy Usage</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-400 rounded-full"></div>
          <span>Renewable %</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 border-t-2 border-dashed border-slate-400"></div>
          <span>Forecast</span>
        </div>
      </div>
    </div>
  )
}
