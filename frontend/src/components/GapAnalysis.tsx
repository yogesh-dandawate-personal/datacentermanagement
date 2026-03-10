/**
 * Gap Analysis Component
 * Displays identified compliance gaps and remediation status
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Button, SkeletonTable } from './ui'
import { AlertTriangle, AlertCircle, ChevronDown, User, Calendar, Zap } from 'lucide-react'
import { ComplianceGap, GapSeverity } from '../types/compliance'

interface GapAnalysisProps {
  gaps: ComplianceGap[] | null
  loading: boolean
}

interface ExpandedGaps {
  [key: string]: boolean
}

export function GapAnalysis({ gaps, loading }: GapAnalysisProps) {
  const [expandedGaps, setExpandedGaps] = useState<ExpandedGaps>({})
  const [selectedSeverity, setSelectedSeverity] = useState<GapSeverity | 'All'>('All')

  const toggleGap = (id: string) => {
    setExpandedGaps((prev) => ({
      ...prev,
      [id]: !prev[id],
    }))
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Gap Analysis</CardTitle>
          <CardDescription>Identified compliance gaps and remediation status</CardDescription>
        </CardHeader>
        <CardContent>
          <SkeletonTable rows={5} cols={4} />
        </CardContent>
      </Card>
    )
  }

  if (!gaps || gaps.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Gap Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-slate-400">No compliance gaps identified</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Filter gaps by severity
  const filteredGaps =
    selectedSeverity === 'All' ? gaps : gaps.filter((g) => g.severity === selectedSeverity)

  // Get severity icon and colors
  const getSeverityIcon = (severity: GapSeverity) => {
    if (severity === 'Critical') {
      return <AlertTriangle className="w-5 h-5 text-red-500" />
    }
    return <AlertCircle className="w-5 h-5 text-yellow-500" />
  }

  const getSeverityColor = (severity: GapSeverity) => {
    switch (severity) {
      case 'Critical':
        return 'bg-red-500/10 border-red-500/20'
      case 'High':
        return 'bg-orange-500/10 border-orange-500/20'
      case 'Medium':
        return 'bg-yellow-500/10 border-yellow-500/20'
      case 'Low':
        return 'bg-blue-500/10 border-blue-500/20'
    }
  }

  const getSeverityBadgeVariant = (severity: GapSeverity) => {
    switch (severity) {
      case 'Critical':
        return 'danger' as const
      case 'High':
        return 'warning' as const
      case 'Medium':
        return 'warning' as const
      case 'Low':
        return 'info' as const
    }
  }

  // Count gaps by severity
  const criticalCount = gaps.filter((g) => g.severity === 'Critical').length
  const highCount = gaps.filter((g) => g.severity === 'High').length
  const mediumCount = gaps.filter((g) => g.severity === 'Medium').length
  const lowCount = gaps.filter((g) => g.severity === 'Low').length

  // Calculate days until deadline
  const daysUntilDeadline = (targetDate: string): number => {
    const today = new Date()
    const deadline = new Date(targetDate)
    const diffTime = deadline.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const getDeadlineStatus = (targetDate: string) => {
    const days = daysUntilDeadline(targetDate)
    if (days < 0) return { text: 'Overdue', color: 'text-red-500' }
    if (days < 30) return { text: `${days} days left`, color: 'text-yellow-500' }
    return { text: `${days} days left`, color: 'text-green-500' }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Gap Analysis</CardTitle>
            <CardDescription>Identified compliance gaps and remediation status</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{gaps.length}</div>
            <p className="text-xs text-slate-400">Total Gaps</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Severity Filter */}
        <div className="flex gap-2 flex-wrap">
          {(['All', 'Critical', 'High', 'Medium', 'Low'] as const).map((severity) => (
            <button
              key={severity}
              onClick={() => setSelectedSeverity(severity)}
              className={`px-4 py-2 rounded-lg border transition-colors text-sm font-medium ${
                selectedSeverity === severity
                  ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                  : 'bg-slate-900/50 border-slate-700/30 text-slate-400 hover:text-slate-300'
              }`}
            >
              {severity === 'All' ? (
                <>All Gaps ({gaps.length})</>
              ) : (
                <>
                  {severity} (
                  {severity === 'Critical'
                    ? criticalCount
                    : severity === 'High'
                      ? highCount
                      : severity === 'Medium'
                        ? mediumCount
                        : lowCount}
                  )
                </>
              )}
            </button>
          ))}
        </div>

        {/* Severity Summary Cards */}
        <div className="grid grid-cols-4 gap-3">
          <Card variant="default" className="bg-red-500/10 border-red-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-red-400 font-medium mb-1">CRITICAL</p>
                <p className="text-2xl font-bold text-red-400">{criticalCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-orange-500/10 border-orange-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-orange-400 font-medium mb-1">HIGH</p>
                <p className="text-2xl font-bold text-orange-400">{highCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-yellow-500/10 border-yellow-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-yellow-400 font-medium mb-1">MEDIUM</p>
                <p className="text-2xl font-bold text-yellow-400">{mediumCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-blue-500/10 border-blue-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-blue-400 font-medium mb-1">LOW</p>
                <p className="text-2xl font-bold text-blue-400">{lowCount}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Gaps List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredGaps.map((gap) => (
            <div
              key={gap.id}
              className={`border rounded-lg transition-all ${getSeverityColor(gap.severity)}`}
            >
              {/* Header Row */}
              <div
                className="p-4 cursor-pointer hover:bg-slate-900/50 transition-colors"
                onClick={() => toggleGap(gap.id)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <ChevronDown
                      className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 mt-0.5 ${
                        expandedGaps[gap.id] ? 'rotate-180' : ''
                      }`}
                    />
                    <div className="flex items-start gap-3 flex-1">
                      {getSeverityIcon(gap.severity)}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-white">
                          {gap.framework} - {gap.requirement}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">{gap.gapDescription}</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 flex-shrink-0">
                    <Badge variant={getSeverityBadgeVariant(gap.severity)}>
                      {gap.severity}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedGaps[gap.id] && (
                <div className="border-t border-slate-700/30 p-4 bg-slate-900/20 space-y-4">
                  {/* Meta Information */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {/* Owner */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <User className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">OWNER</p>
                      </div>
                      <p className="text-sm text-white">{gap.owner}</p>
                      {gap.ownerEmail && (
                        <p className="text-xs text-slate-500">{gap.ownerEmail}</p>
                      )}
                    </div>

                    {/* Target Date */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">TARGET DATE</p>
                      </div>
                      <p className="text-sm text-white">
                        {new Date(gap.targetRemediationDate).toLocaleDateString()}
                      </p>
                      <p className={`text-xs mt-1 font-medium ${getDeadlineStatus(gap.targetRemediationDate).color}`}>
                        {getDeadlineStatus(gap.targetRemediationDate).text}
                      </p>
                    </div>

                    {/* Identified Date */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">IDENTIFIED</p>
                      </div>
                      <p className="text-sm text-white">
                        {new Date(gap.identifiedDate).toLocaleDateString()}
                      </p>
                    </div>

                    {/* Related Tasks */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">TASKS</p>
                      </div>
                      <p className="text-sm text-white">{gap.relatedTasks.length} tasks assigned</p>
                    </div>
                  </div>

                  {/* Evidence Documents */}
                  {gap.evidence && gap.evidence.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 mb-2">EVIDENCE</h4>
                      <div className="flex flex-wrap gap-2">
                        {gap.evidence.map((doc) => (
                          <button
                            key={doc}
                            className="px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 rounded text-xs text-cyan-400 transition-colors"
                          >
                            View Document
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2 border-t border-slate-700/30">
                    <Button size="sm" variant="outline" className="flex-1">
                      View Related Tasks
                    </Button>
                    <Button size="sm" variant="primary" className="flex-1">
                      Update Remediation
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredGaps.length === 0 && (
          <div className="text-center py-8">
            <p className="text-slate-400">No gaps match the selected severity level</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
