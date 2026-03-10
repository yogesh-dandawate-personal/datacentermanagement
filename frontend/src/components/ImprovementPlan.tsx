/**
 * ImprovementPlan Component
 * AI-generated improvement recommendations with impact estimates
 */

import { Lightbulb, TrendingUp, DollarSign, Clock, Target } from 'lucide-react'
import { Card } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import type { ImprovementRecommendation } from '../services/api'

interface ImprovementPlanProps {
  recommendations: ImprovementRecommendation[]
}

export function ImprovementPlan({ recommendations }: ImprovementPlanProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <Card>
        <div className="p-12 text-center text-slate-500">
          <Lightbulb className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No recommendations available</p>
        </div>
      </Card>
    )
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'energy':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'emissions':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      case 'renewable':
        return 'text-green-400 bg-green-500/10 border-green-500/30'
      case 'efficiency':
        return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30'
      default:
        return 'text-slate-400 bg-slate-500/10 border-slate-500/30'
    }
  }

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return <Badge variant="success" size="sm">Easy</Badge>
      case 'medium':
        return <Badge variant="warning" size="sm">Medium</Badge>
      case 'hard':
        return <Badge variant="danger" size="sm">Hard</Badge>
      default:
        return <Badge variant="secondary" size="sm">{difficulty}</Badge>
    }
  }

  // Sort by priority score (descending)
  const sortedRecommendations = [...recommendations].sort((a, b) => b.priority_score - a.priority_score)

  return (
    <Card>
      <div className="p-6 border-b border-slate-700/30">
        <h3 className="text-xl font-semibold text-white flex items-center gap-2">
          <Lightbulb className="w-6 h-6 text-yellow-400" />
          Improvement Recommendations
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          AI-powered suggestions to improve sustainability performance
        </p>
      </div>

      <div className="p-6 space-y-4 max-h-[600px] overflow-y-auto">
        {sortedRecommendations.map((rec) => (
          <div
            key={rec.id}
            className="border border-slate-700/50 rounded-lg p-5 hover:bg-slate-800/30 transition group"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="text-lg font-semibold text-white group-hover:text-cyan-400 transition">
                    {rec.title}
                  </h4>
                  <Badge
                    variant="primary"
                    size="sm"
                    className={getCategoryColor(rec.category)}
                  >
                    {rec.category}
                  </Badge>
                </div>
                <p className="text-sm text-slate-400">{rec.description}</p>
              </div>
              <div className="ml-4">
                <div className="text-right mb-2">
                  <p className="text-2xl font-bold text-cyan-400">{rec.priority_score}</p>
                  <p className="text-xs text-slate-500">Priority</p>
                </div>
                {getDifficultyBadge(rec.difficulty)}
              </div>
            </div>

            {/* Impact Metrics */}
            <div className="grid grid-cols-3 gap-4 bg-slate-800/40 rounded-lg p-4 mt-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp className="w-4 h-4 text-green-400" />
                  <p className="text-xs text-slate-400">Emissions Reduction</p>
                </div>
                <p className="text-lg font-bold text-green-400">
                  {rec.estimated_impact.emissions_reduction_percent}%
                </p>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <DollarSign className="w-4 h-4 text-cyan-400" />
                  <p className="text-xs text-slate-400">Annual Savings</p>
                </div>
                <p className="text-lg font-bold text-cyan-400">
                  ${rec.estimated_impact.cost_savings_usd.toLocaleString()}
                </p>
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-yellow-400" />
                  <p className="text-xs text-slate-400">Payback Period</p>
                </div>
                <p className="text-lg font-bold text-yellow-400">
                  {rec.estimated_impact.payback_months} mo
                </p>
              </div>
            </div>

            {/* Action Button */}
            <div className="mt-4 flex gap-2">
              <Button variant="outline" size="sm" fullWidth>
                View Details
              </Button>
              <Button variant="primary" size="sm" fullWidth icon={<Target className="w-4 h-4" />}>
                Create Action Plan
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="p-6 border-t border-slate-700/30 bg-gradient-to-br from-blue-500/5 to-cyan-500/5">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-white">{recommendations.length}</p>
            <p className="text-xs text-slate-400 mt-1">Total Recommendations</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-400">
              {recommendations
                .reduce((sum, r) => sum + r.estimated_impact.emissions_reduction_percent, 0)
                .toFixed(0)}
              %
            </p>
            <p className="text-xs text-slate-400 mt-1">Total Impact</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-cyan-400">
              ${recommendations
                .reduce((sum, r) => sum + r.estimated_impact.cost_savings_usd, 0)
                .toLocaleString()}
            </p>
            <p className="text-xs text-slate-400 mt-1">Total Savings</p>
          </div>
        </div>
      </div>
    </Card>
  )
}
