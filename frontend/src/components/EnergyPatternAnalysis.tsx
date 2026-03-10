/**
 * EnergyPatternAnalysis Component
 * Peak detection and anomaly visualization for energy usage patterns
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AlertTriangle, TrendingUp, Clock } from 'lucide-react'
import type { EnergyPattern } from '../services/api'

interface EnergyPatternAnalysisProps {
  patterns: EnergyPattern[]
}

export function EnergyPatternAnalysis({ patterns }: EnergyPatternAnalysisProps) {
  if (!patterns || patterns.length === 0) {
    return (
      <div className="flex items-center justify-center h-80 text-slate-500">
        No energy pattern data available
      </div>
    )
  }

  // Calculate statistics
  const peakCount = patterns.filter((p) => p.is_peak).length
  const anomalyCount = patterns.filter((p) => (p.anomaly_score || 0) > 0.7).length
  const avgUsage = patterns.reduce((sum, p) => sum + p.usage_kw, 0) / patterns.length
  const maxUsage = Math.max(...patterns.map((p) => p.usage_kw))

  // Format data for chart (sample every 2 hours to avoid clutter)
  const chartData = patterns
    .filter((_, index) => index % 2 === 0)
    .map((pattern) => ({
      time: new Date(pattern.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      }),
      usage: pattern.usage_kw,
      isPeak: pattern.is_peak,
      isAnomaly: (pattern.anomaly_score || 0) > 0.7,
    }))

  // Identify peak hours
  const peakHours = patterns
    .filter((p) => p.is_peak)
    .map((p) => new Date(p.timestamp).getHours())
    .filter((hour, index, arr) => arr.indexOf(hour) === index)
    .sort((a, b) => a - b)

  return (
    <div className="space-y-4">
      {/* Statistics Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-blue-400" />
            <p className="text-xs text-blue-300 uppercase tracking-wide">Peak Events</p>
          </div>
          <p className="text-2xl font-bold text-white">{peakCount}</p>
          <p className="text-xs text-slate-400 mt-1">in 30 days</p>
        </div>

        <div className="bg-gradient-to-br from-amber-500/10 to-orange-600/10 border border-amber-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <p className="text-xs text-amber-300 uppercase tracking-wide">Anomalies</p>
          </div>
          <p className="text-2xl font-bold text-white">{anomalyCount}</p>
          <p className="text-xs text-slate-400 mt-1">detected</p>
        </div>

        <div className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/10 border border-cyan-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <p className="text-xs text-cyan-300 uppercase tracking-wide">Avg Usage</p>
          </div>
          <p className="text-2xl font-bold text-white">
            {avgUsage.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </p>
          <p className="text-xs text-slate-400 mt-1">kW</p>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />

          <XAxis
            dataKey="time"
            stroke="#94a3b8"
            style={{ fontSize: '11px' }}
            tick={{ fill: '#94a3b8' }}
            interval={Math.floor(chartData.length / 8)} // Show ~8 labels
          />

          <YAxis
            stroke="#94a3b8"
            style={{ fontSize: '12px' }}
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Usage (kW)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '12px',
            }}
            labelStyle={{ color: '#f1f5f9', fontWeight: 'bold', marginBottom: '4px' }}
            itemStyle={{ color: '#cbd5e1', fontSize: '13px' }}
            formatter={(value: number) => [
              `${value.toLocaleString()} kW`,
              'Usage',
            ]}
          />

          <Bar dataKey="usage" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  entry.isAnomaly
                    ? '#f59e0b' // Amber for anomalies
                    : entry.isPeak
                    ? '#ef4444' // Red for peaks
                    : '#3b82f6' // Blue for normal
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Peak Hours Info */}
      {peakHours.length > 0 && (
        <div className="bg-slate-800/30 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Peak Usage Hours
          </h4>
          <div className="flex flex-wrap gap-2">
            {peakHours.map((hour) => (
              <span
                key={hour}
                className="px-3 py-1 bg-red-500/20 border border-red-500/30 text-red-300 rounded-full text-xs font-medium"
              >
                {hour.toString().padStart(2, '0')}:00
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Consider load shifting during these hours to reduce peak demand charges
          </p>
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span>Normal Usage</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span>Peak Events</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-amber-500 rounded"></div>
          <span>Anomalies</span>
        </div>
      </div>
    </div>
  )
}
