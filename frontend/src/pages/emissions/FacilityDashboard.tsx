/**
 * Emissions Facility Dashboard
 * Real-time emissions monitoring with Scope 1/2/3 breakdown,
 * carbon intensity, KPIs, and 30-day trend analysis
 */

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Button, Alert, Spinner, Badge } from '@/components/ui'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingDown, TrendingUp, AlertCircle, RefreshCw, Download, Filter } from 'lucide-react'
import { useFacilityEmissions } from '@/hooks/useEmissions'

export default function FacilityDashboard() {
  const { facilityId } = useParams<{ facilityId: string }>()
  const [period, setPeriod] = useState('current_month')
  const { data, loading, error } = useFacilityEmissions(facilityId || '', period)

  if (!facilityId) {
    return (
      <Alert variant="error">
        <AlertCircle className="w-5 h-5" />
        Facility ID is required
      </Alert>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="error">
        <AlertCircle className="w-5 h-5" />
        {error}
      </Alert>
    )
  }

  if (!data) {
    return (
      <Alert variant="warning">
        <AlertCircle className="w-5 h-5" />
        No emissions data available for this facility
      </Alert>
    )
  }

  const scopeColors = ['#ef4444', '#f97316', '#eab308']
  const breakdownData = data.breakdown || []

  // Determine trend direction
  const momChange = data.metrics?.mom_change_pct || 0
  const trendingUp = momChange > 0
  const TrendIcon = trendingUp ? TrendingUp : TrendingDown
  const trendColor = trendingUp ? 'text-red-400' : 'text-green-400'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Facility Emissions Dashboard</h1>
          <p className="text-slate-400 mt-1">Real-time emissions monitoring and analysis</p>
        </div>

        <div className="flex gap-2">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
          >
            <option value="current_month">Current Month</option>
            <option value="current_year">Current Year</option>
            <option value="last_30_days">Last 30 Days</option>
            <option value="last_90_days">Last 90 Days</option>
          </select>

          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4" />
          </Button>

          <Button variant="outline" size="sm">
            <Download className="w-4 h-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Emissions */}
        <Card>
          <div className="flex items-start justify-between mb-3">
            <div>
              <p className="text-sm text-slate-400">Total Emissions (MTD)</p>
              <p className="text-3xl font-bold mt-1">{data.emissions.total_tco2e.toFixed(1)}</p>
              <p className="text-xs text-slate-500 mt-1">tCO2e</p>
            </div>
            <div className={`w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center ${trendColor}`}>
              <TrendIcon className="w-6 h-6" />
            </div>
          </div>
          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs ${trendingUp ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'}`}>
            {trendingUp ? '+' : ''}
            {Math.abs(momChange).toFixed(1)}% MoM
          </div>
        </Card>

        {/* Carbon Intensity */}
        <Card>
          <p className="text-sm text-slate-400">Carbon Intensity</p>
          <p className="text-3xl font-bold mt-2">{data.metrics.carbon_intensity_gco2e_kwh.toFixed(0)}</p>
          <p className="text-xs text-slate-500 mt-1">gCO2e/kWh</p>
          <p className="text-xs text-slate-500 mt-2">Industry avg: 425</p>
        </Card>

        {/* PUE */}
        <Card>
          <p className="text-sm text-slate-400">PUE (Power Usage Efficiency)</p>
          <p className="text-3xl font-bold mt-2">{data.metrics.pue?.toFixed(2) || 'N/A'}</p>
          <p className="text-xs text-slate-500 mt-2">Target: 1.20</p>
        </Card>

        {/* Renewable Energy */}
        <Card>
          <p className="text-sm text-slate-400">Renewable Energy</p>
          <div className="mt-2">
            <p className="text-3xl font-bold">{data.metrics.renewable_pct.toFixed(0)}%</p>
            <div className="w-full bg-slate-700 rounded-full h-2 mt-3">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${data.metrics.renewable_pct}%` }}
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Emissions Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Pie Chart */}
        <Card className="lg:col-span-1">
          <h2 className="text-lg font-semibold mb-4">Emissions Breakdown</h2>
          {breakdownData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={breakdownData}
                  dataKey="emissions_tco2e"
                  nameKey="scope"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={(entry) => `${entry.pct.toFixed(0)}%`}
                >
                  {breakdownData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={scopeColors[index]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${value.toFixed(2)} tCO2e`} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-400 h-32 flex items-center">No breakdown data available</p>
          )}
        </Card>

        {/* Scope Details Table */}
        <Card className="lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Emissions by Scope</h2>
          <div className="space-y-3">
            {breakdownData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: scopeColors[index] }}
                  />
                  <div>
                    <p className="font-medium">{item.scope}</p>
                    <p className="text-xs text-slate-400">Greenhouse gas emissions</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{item.emissions_tco2e.toFixed(2)}</p>
                  <p className="text-xs text-slate-400">{item.pct.toFixed(1)}% of total</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 30-Day Trend */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">30-Day Emissions Trend</h2>
        {data.trend_30d && data.trend_30d.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trend_30d}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tick={{ fontSize: 12 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
                formatter={(value) => `${(value as number).toFixed(2)} tCO2e`}
              />
              <Legend />
              <Line type="monotone" dataKey="scope_1" stroke="#ef4444" name="Scope 1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="scope_2" stroke="#f97316" name="Scope 2" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="scope_3" stroke="#eab308" name="Scope 3" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-slate-400 h-64 flex items-center justify-center">No trend data available</p>
        )}
      </Card>

      {/* Top Emitting Sources */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Top Emitting Assets</h2>
        {data.top_sources && data.top_sources.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Asset Name</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Type</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Emissions</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">% of Total</th>
                </tr>
              </thead>
              <tbody>
                {data.top_sources.map((source, index) => (
                  <tr key={source.source_id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition">
                    <td className="py-3 px-4">{source.source_name}</td>
                    <td className="py-3 px-4">
                      <Badge variant="outline" className="text-xs">
                        {source.source_type}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      {source.emissions_tco2e.toFixed(2)} tCO2e
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <div className="w-16 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${Math.min(source.emissions_tco2e / (data.emissions.total_tco2e / 100), 100)}%` }}
                          />
                        </div>
                        <span className="text-xs w-10 text-right">
                          {((source.emissions_tco2e / data.emissions.total_tco2e) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-slate-400">No source data available</p>
        )}
      </Card>

      {/* Data Quality Notice */}
      <Card className="bg-blue-950/30 border border-blue-500/30">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-blue-300">Data Quality</p>
            <p className="text-sm text-blue-200/80 mt-1">
              Data calculated from {data.calculation_count} calculation records. Last updated: {data.date_range?.end || 'N/A'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
