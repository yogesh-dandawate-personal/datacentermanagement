/**
 * Compliance Score Widget
 * Displays overall compliance score with framework breakdown
 */

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, SkeletonChart } from './ui'
import { TrendingUp, AlertCircle } from 'lucide-react'
import { ComplianceScore as ComplianceScoreType } from '../types/compliance'

interface ComplianceScoreProps {
  data: ComplianceScoreType | null
  loading: boolean
}

export function ComplianceScore({ data, loading }: ComplianceScoreProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Compliance Score Trend</CardTitle>
          <CardDescription>Overall compliance performance over time</CardDescription>
        </CardHeader>
        <CardContent>
          <SkeletonChart height={300} />
        </CardContent>
      </Card>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Compliance Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-slate-400">No data available</div>
        </CardContent>
      </Card>
    )
  }

  // Score color coding
  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-500/10 border-green-500/20'
    if (score >= 60) return 'bg-yellow-500/10 border-yellow-500/20'
    return 'bg-red-500/10 border-red-500/20'
  }

  const filteredTrend = data.trend.filter((d) => d)

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <Card className={`border ${getScoreBgColor(data.overallScore)}`}>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Main Score */}
            <div className="md:col-span-1 flex flex-col items-center justify-center">
              <div className="text-center">
                <div className="text-5xl font-bold mb-2">
                  <span className={getScoreColor(data.overallScore)}>{data.overallScore}</span>
                  <span className="text-2xl text-slate-400">/100</span>
                </div>
                <p className="text-sm text-slate-400">Overall Score</p>
              </div>
            </div>

            {/* Framework Breakdown */}
            <div className="md:col-span-3 grid grid-cols-3 gap-4">
              {/* GRI Score */}
              <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                  <span className="text-xs font-medium text-slate-400">GRI</span>
                </div>
                <div className="text-2xl font-bold text-white">{data.griScore}</div>
                <div className="text-xs text-slate-500">GRI Standards</div>
              </div>

              {/* TCFD Score */}
              <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                  <span className="text-xs font-medium text-slate-400">TCFD</span>
                </div>
                <div className="text-2xl font-bold text-white">{data.tcfdScore}</div>
                <div className="text-xs text-slate-500">TCFD Framework</div>
              </div>

              {/* CDP Score */}
              <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="text-xs font-medium text-slate-400">CDP</span>
                </div>
                <div className="text-2xl font-bold text-white">{data.cdpScore}</div>
                <div className="text-xs text-slate-500">CDP Disclosure</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Score Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            Compliance Score Trend
          </CardTitle>
          <CardDescription>12-month performance trajectory</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={filteredTrend} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" style={{ fontSize: '12px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '12px' }} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #64748b',
                    borderRadius: '8px',
                    padding: '8px 12px',
                  }}
                  labelStyle={{ color: '#f1f5f9' }}
                  formatter={(value) => `${value}%`}
                />
                <Legend wrapperStyle={{ paddingTop: '20px', color: '#cbd5e1' }} />
                <Line
                  type="monotone"
                  dataKey="overallScore"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Overall Score"
                />
                <Line
                  type="monotone"
                  dataKey="griScore"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  dot={false}
                  name="GRI Score"
                />
                <Line
                  type="monotone"
                  dataKey="tcfdScore"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  name="TCFD Score"
                />
                <Line
                  type="monotone"
                  dataKey="cdpScore"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                  name="CDP Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Score Interpretation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-blue-500" />
            Score Interpretation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
              <div>
                <p className="text-sm font-medium text-white">80-100: Excellent</p>
                <p className="text-xs text-slate-400">Full compliance with comprehensive programs</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-yellow-500 mt-2"></div>
              <div>
                <p className="text-sm font-medium text-white">60-79: Good</p>
                <p className="text-xs text-slate-400">Substantial compliance with some gaps</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-red-500 mt-2"></div>
              <div>
                <p className="text-sm font-medium text-white">0-59: Needs Improvement</p>
                <p className="text-xs text-slate-400">Significant gaps requiring immediate action</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
