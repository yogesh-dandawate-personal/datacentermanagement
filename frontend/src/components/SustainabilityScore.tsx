/**
 * SustainabilityScore Component
 * Composite sustainability score with breakdown by category
 */

import { TrendingUp, TrendingDown, Minus, Award, Zap, Leaf, Target, CheckCircle } from 'lucide-react'
import { Card } from './ui/Card'
import type { SustainabilityScore as SustainabilityScoreType } from '../services/api'

interface SustainabilityScoreProps {
  score: SustainabilityScoreType
}

export function SustainabilityScore({ score }: SustainabilityScoreProps) {
  const { overall_score, breakdown, trend, industry_percentile } = score

  // Determine score color and grade
  const getScoreColor = (value: number) => {
    if (value >= 80) return 'text-green-400'
    if (value >= 60) return 'text-cyan-400'
    if (value >= 40) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreGrade = (value: number) => {
    if (value >= 90) return 'A+'
    if (value >= 80) return 'A'
    if (value >= 70) return 'B'
    if (value >= 60) return 'C'
    if (value >= 50) return 'D'
    return 'F'
  }

  const getTrendIcon = () => {
    if (trend === 'improving') return <TrendingUp className="w-5 h-5 text-green-400" />
    if (trend === 'declining') return <TrendingDown className="w-5 h-5 text-red-400" />
    return <Minus className="w-5 h-5 text-slate-400" />
  }

  const getTrendColor = () => {
    if (trend === 'improving') return 'text-green-400 bg-green-500/10 border-green-500/30'
    if (trend === 'declining') return 'text-red-400 bg-red-500/10 border-red-500/30'
    return 'text-slate-400 bg-slate-500/10 border-slate-500/30'
  }

  const breakdownItems = [
    {
      label: 'Energy Efficiency',
      value: breakdown.energy_efficiency,
      icon: Zap,
      color: 'text-yellow-400',
    },
    {
      label: 'Renewable Usage',
      value: breakdown.renewable_usage,
      icon: Leaf,
      color: 'text-green-400',
    },
    {
      label: 'Emissions Reduction',
      value: breakdown.emissions_reduction,
      icon: Target,
      color: 'text-cyan-400',
    },
    {
      label: 'Compliance Adherence',
      value: breakdown.compliance_adherence,
      icon: CheckCircle,
      color: 'text-blue-400',
    },
  ]

  return (
    <Card className="bg-gradient-to-br from-slate-800/60 to-slate-900/60">
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Overall Score */}
          <div className="md:col-span-1 flex flex-col items-center justify-center bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30 rounded-xl p-6">
            <div className="flex items-center gap-2 mb-2">
              <Award className="w-6 h-6 text-blue-400" />
              <p className="text-sm text-slate-300 font-medium">Sustainability Score</p>
            </div>

            <div className="relative w-32 h-32 mb-3">
              {/* Circular Progress */}
              <svg className="transform -rotate-90 w-32 h-32">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="#334155"
                  strokeWidth="8"
                  fill="none"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  stroke="url(#scoreGradient)"
                  strokeWidth="8"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={`${(overall_score / 100) * 352} 352`}
                  className="transition-all duration-1000"
                />
                <defs>
                  <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#22d3ee" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Score Text */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className={`text-4xl font-bold ${getScoreColor(overall_score)}`}>
                    {overall_score}
                  </p>
                  <p className="text-xs text-slate-400">out of 100</p>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className={`text-2xl font-bold ${getScoreColor(overall_score)} mb-1`}>
                Grade {getScoreGrade(overall_score)}
              </p>
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${getTrendColor()}`}>
                {getTrendIcon()}
                <span className="text-xs font-medium capitalize">{trend}</span>
              </div>
            </div>
          </div>

          {/* Breakdown */}
          <div className="md:col-span-2 space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Score Breakdown</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {breakdownItems.map((item) => {
                  const Icon = item.icon
                  return (
                    <div
                      key={item.label}
                      className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-4 hover:bg-slate-800/60 transition"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Icon className={`w-4 h-4 ${item.color}`} />
                          <span className="text-sm text-slate-300 font-medium">{item.label}</span>
                        </div>
                        <span className={`text-lg font-bold ${getScoreColor(item.value)}`}>
                          {item.value}
                        </span>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full bg-slate-700/30 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            item.value >= 80
                              ? 'bg-gradient-to-r from-green-500 to-green-400'
                              : item.value >= 60
                              ? 'bg-gradient-to-r from-cyan-500 to-cyan-400'
                              : item.value >= 40
                              ? 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                              : 'bg-gradient-to-r from-red-500 to-red-400'
                          }`}
                          style={{ width: `${item.value}%` }}
                        ></div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Industry Comparison */}
            <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-200 font-medium mb-1">Industry Ranking</p>
                  <p className="text-xs text-slate-400">
                    Your organization ranks in the top{' '}
                    <span className="text-purple-300 font-semibold">{100 - industry_percentile}%</span>{' '}
                    of your industry
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-purple-400">{industry_percentile}th</p>
                  <p className="text-xs text-slate-400">percentile</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
