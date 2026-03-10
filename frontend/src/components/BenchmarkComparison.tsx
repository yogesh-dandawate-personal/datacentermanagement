/**
 * BenchmarkComparison Component
 * Compare organization metrics against industry averages and best practices
 */

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, Award, Target } from 'lucide-react'
import { Card } from './ui/Card'
import { Badge } from './ui/Badge'
import type { BenchmarkData, PeerComparison } from '../services/api'

interface BenchmarkComparisonProps {
  benchmarks: BenchmarkData
  peerComparison: PeerComparison
}

export function BenchmarkComparison({ benchmarks, peerComparison }: BenchmarkComparisonProps) {
  const { your_organization, industry_average, industry_best } = benchmarks

  // Format data for comparison chart
  const comparisonData = [
    {
      metric: 'Emissions Intensity',
      your: your_organization.emissions_intensity,
      average: industry_average.emissions_intensity,
      best: industry_best.emissions_intensity,
    },
    {
      metric: 'Energy Intensity',
      your: your_organization.energy_intensity,
      average: industry_average.energy_intensity,
      best: industry_best.energy_intensity,
    },
    {
      metric: 'Renewable %',
      your: your_organization.renewable_percentage,
      average: industry_average.renewable_percentage,
      best: industry_best.renewable_percentage,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-cyan-500/10 to-cyan-600/10 border-cyan-500/30">
          <div className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              <p className="text-sm text-cyan-300 font-medium">Your Performance</p>
            </div>
            <p className="text-3xl font-bold text-white mb-1">
              {your_organization.emissions_intensity.toFixed(1)}
            </p>
            <p className="text-xs text-slate-400">tCO₂e per $M revenue</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border-blue-500/30">
          <div className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-blue-400" />
              <p className="text-sm text-blue-300 font-medium">Industry Average</p>
            </div>
            <p className="text-3xl font-bold text-white mb-1">
              {industry_average.emissions_intensity.toFixed(1)}
            </p>
            <p className="text-xs text-slate-400">tCO₂e per $M revenue</p>
          </div>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/10 border-green-500/30">
          <div className="p-6">
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-5 h-5 text-green-400" />
              <p className="text-sm text-green-300 font-medium">Industry Best</p>
            </div>
            <p className="text-3xl font-bold text-white mb-1">
              {industry_best.emissions_intensity.toFixed(1)}
            </p>
            <p className="text-xs text-slate-400">tCO₂e per $M revenue</p>
          </div>
        </Card>
      </div>

      {/* Peer Ranking */}
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">Peer Ranking</h3>
              <p className="text-sm text-slate-400 mt-1">Your position among industry peers</p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-bold text-cyan-400">{peerComparison.your_percentile}th</p>
              <p className="text-sm text-slate-400">percentile</p>
              <Badge variant="success" size="sm">
                Top {100 - peerComparison.your_percentile}%
              </Badge>
            </div>
          </div>
        </div>
        <div className="p-6">
          <p className="text-sm text-slate-300 mb-4">
            You rank <span className="font-semibold text-cyan-400">#{peerComparison.your_position}</span> out of{' '}
            <span className="font-semibold">{peerComparison.total_peers}</span> organizations in your industry
          </p>
          <div className="bg-slate-800/30 rounded-full h-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-cyan-400 transition-all duration-1000"
              style={{ width: `${peerComparison.your_percentile}%` }}
            ></div>
          </div>
        </div>
      </Card>

      {/* Comparison Chart */}
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <h3 className="text-xl font-semibold text-white">Performance Comparison</h3>
          <p className="text-sm text-slate-400 mt-1">Key metrics vs. industry benchmarks</p>
        </div>
        <div className="p-6">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="metric" stroke="#94a3b8" style={{ fontSize: '12px' }} tick={{ fill: '#94a3b8' }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} tick={{ fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  padding: '12px',
                }}
                labelStyle={{ color: '#f1f5f9', fontWeight: 'bold' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="your" name="Your Organization" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              <Bar dataKey="average" name="Industry Average" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="best" name="Industry Best" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}
