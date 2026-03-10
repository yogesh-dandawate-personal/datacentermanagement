/**
 * Target Tracking Component
 * Displays progress towards emissions reduction and KPI targets
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, SkeletonChart } from './ui'
import { Target, Zap, Droplets, Wind, Activity } from 'lucide-react'
import { TargetTrackingData, KPITarget } from '../types/compliance'

interface TargetTrackingProps {
  targets: TargetTrackingData[] | null
  kpiTargets: KPITarget[] | null
  loading: boolean
}

export function TargetTracking({ targets, kpiTargets, loading }: TargetTrackingProps) {
  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Target Tracking</CardTitle>
          </CardHeader>
          <CardContent>
            <SkeletonChart height={300} />
          </CardContent>
        </Card>
      </div>
    )
  }

  const getStatusBgColor = (status: string) => {
    if (status === 'On Track') return 'bg-green-500/10 border-green-500/20'
    if (status === 'At Risk') return 'bg-yellow-500/10 border-yellow-500/20'
    return 'bg-red-500/10 border-red-500/20'
  }

  const getKPIIcon = (code: string) => {
    switch (code) {
      case 'PUE':
        return <Zap className="w-5 h-5 text-blue-400" />
      case 'CUE':
        return <Wind className="w-5 h-5 text-cyan-400" />
      case 'WUE':
        return <Droplets className="w-5 h-5 text-blue-500" />
      case 'ERE':
        return <Activity className="w-5 h-5 text-green-400" />
      default:
        return <Target className="w-5 h-5 text-slate-400" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Emissions Reduction Targets */}
      {targets && targets.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              Strategic Targets Progress
            </CardTitle>
            <CardDescription>Track progress towards organizational targets</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {targets.map((target) => {
              const filteredTrend = target.trend.filter((d) => d)
              const latestData = filteredTrend[filteredTrend.length - 1]

              return (
                <div key={target.id} className="space-y-4">
                  {/* Target Header */}
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-sm font-semibold text-white">{target.name}</h3>
                      <p className="text-xs text-slate-400">{target.framework}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-white">
                        {latestData?.value !== undefined ? latestData.value : target.currentValue}
                        <span className="text-sm text-slate-400 ml-1">{target.targetUnit}</span>
                      </div>
                      <p className="text-xs text-slate-400">
                        Target: {target.targetValue} {target.targetUnit}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Progress: {target.progressPercentage}%</span>
                      <span>Target: {target.targetDate}</span>
                    </div>
                    <div className="h-3 bg-slate-900/50 rounded-full overflow-hidden border border-slate-700/30">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
                        style={{ width: `${target.progressPercentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Trend Chart */}
                  {filteredTrend.length > 0 && (
                    <div className="h-40">
                      <ResponsiveContainer width="100%" height={160}>
                        <LineChart data={filteredTrend} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                          <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '11px' }} />
                          <YAxis stroke="#64748b" style={{ fontSize: '11px' }} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#0f172a',
                              border: '1px solid #64748b',
                              borderRadius: '8px',
                              padding: '8px 12px',
                              fontSize: '12px',
                            }}
                            labelStyle={{ color: '#f1f5f9' }}
                            formatter={(value) => (value ? `${value} ${target.targetUnit}` : null)}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            dot={false}
                            name="Actual"
                          />
                          <Line
                            type="monotone"
                            dataKey="forecast"
                            stroke="#06b6d4"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="Forecast"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              )
            })}
          </CardContent>
        </Card>
      )}

      {/* KPI Targets */}
      {kpiTargets && kpiTargets.length > 0 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-500" />
              Datacenter KPI Targets
            </h2>
          </div>

          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {kpiTargets.map((kpi) => {
              const progressPercentage = (kpi.progress || 0)
              const needsAttention = kpi.status !== 'On Track'

              return (
                <Card
                  key={kpi.kpiCode}
                  className={`border ${needsAttention ? getStatusBgColor(kpi.status) : 'border-slate-700/30'}`}
                >
                  <CardContent className="pt-6">
                    {/* KPI Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-3">
                        {getKPIIcon(kpi.kpiCode)}
                        <div>
                          <h3 className="text-sm font-semibold text-white">{kpi.kpiName}</h3>
                          <p className="text-xs text-slate-400">{kpi.kpiCode}</p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        kpi.status === 'On Track'
                          ? 'bg-green-500/20 text-green-300'
                          : kpi.status === 'At Risk'
                            ? 'bg-yellow-500/20 text-yellow-300'
                            : 'bg-red-500/20 text-red-300'
                      }`}>
                        {kpi.status}
                      </div>
                    </div>

                    {/* Values */}
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div>
                        <p className="text-xs text-slate-400 mb-1">Current</p>
                        <p className="text-lg font-bold text-white">{kpi.currentValue}</p>
                        <p className="text-xs text-slate-500">{kpi.targetUnit}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400 mb-1">Target</p>
                        <p className="text-lg font-bold text-cyan-400">{kpi.targetValue}</p>
                        <p className="text-xs text-slate-500">{kpi.targetUnit}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400 mb-1">Standard</p>
                        <p className="text-lg font-bold text-slate-300">{kpi.standardValue}</p>
                        <p className="text-xs text-slate-500">{kpi.targetUnit}</p>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Progress to Target</span>
                        <span className="text-white font-medium">{progressPercentage}%</span>
                      </div>
                      <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden border border-slate-700/30">
                        <div
                          className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
                          style={{ width: `${progressPercentage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Historical Data Chart */}
                    {kpi.historicalData && kpi.historicalData.length > 0 && (
                      <div className="h-32 -mx-6 mb-4">
                        <ResponsiveContainer width="100%" height={128}>
                          <BarChart data={kpi.historicalData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                            <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '10px' }} />
                            <YAxis stroke="#64748b" style={{ fontSize: '10px' }} />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: '#0f172a',
                                border: '1px solid #64748b',
                                borderRadius: '8px',
                                padding: '8px 12px',
                                fontSize: '11px',
                              }}
                              formatter={(value) => `${value} ${kpi.targetUnit}`}
                            />
                            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* Forecast */}
                    {kpi.forecastedValue && kpi.forecastDate && (
                      <div className="p-3 bg-slate-900/50 rounded border border-slate-700/30 text-xs">
                        <p className="text-slate-400 mb-1">Projected Performance</p>
                        <p className="text-white font-semibold">
                          {kpi.forecastedValue} {kpi.targetUnit} by {new Date(kpi.forecastDate).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
