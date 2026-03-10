/**
 * Compliance Matrix Component
 * Displays GRI/TCFD/CDP framework requirements and their status
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Button, SkeletonTable } from './ui'
import { ChevronDown, Check, Clock, X, FileText, Info } from 'lucide-react'
import { ComplianceMatrix as ComplianceMatrixType, RequirementStatus, Framework } from '../types/compliance'

interface ComplianceMatrixProps {
  data: ComplianceMatrixType | null
  loading: boolean
  framework: Framework
}

interface ExpandedRow {
  [key: string]: boolean
}

export function ComplianceMatrix({ data, loading, framework }: ComplianceMatrixProps) {
  const [expandedRows, setExpandedRows] = useState<ExpandedRow>({})

  const toggleRow = (id: string) => {
    setExpandedRows((prev) => ({
      ...prev,
      [id]: !prev[id],
    }))
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{framework} Compliance Matrix</CardTitle>
          <CardDescription>Framework requirements and completion status</CardDescription>
        </CardHeader>
        <CardContent>
          <SkeletonTable rows={5} cols={4} />
        </CardContent>
      </Card>
    )
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{framework} Compliance Matrix</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-slate-400">No data available</div>
        </CardContent>
      </Card>
    )
  }

  const getStatusIcon = (status: RequirementStatus) => {
    switch (status) {
      case 'Complete':
        return <Check className="w-5 h-5 text-green-400" />
      case 'In Progress':
        return <Clock className="w-5 h-5 text-yellow-400" />
      case 'Not Started':
        return <X className="w-5 h-5 text-red-400" />
    }
  }

  const getStatusColor = (status: RequirementStatus) => {
    switch (status) {
      case 'Complete':
        return 'bg-green-500/10 border-green-500/20'
      case 'In Progress':
        return 'bg-yellow-500/10 border-yellow-500/20'
      case 'Not Started':
        return 'bg-red-500/10 border-red-500/20'
    }
  }

  const getStatusBadgeVariant = (status: RequirementStatus) => {
    switch (status) {
      case 'Complete':
        return 'success' as const
      case 'In Progress':
        return 'warning' as const
      case 'Not Started':
        return 'danger' as const
    }
  }

  // Calculate progress bar width
  const completePercentage = (data.complete / data.totalRequirements) * 100
  const inProgressPercentage = (data.inProgress / data.totalRequirements) * 100
  const notStartedPercentage = (data.notStarted / data.totalRequirements) * 100

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>{framework} Compliance Matrix</CardTitle>
            <CardDescription>Framework requirements and completion status</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{data.completionPercentage}%</div>
            <p className="text-xs text-slate-400">Complete</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Overall Progress</span>
            <span className="text-white font-medium">
              {data.complete} of {data.totalRequirements} requirements complete
            </span>
          </div>
          <div className="flex h-3 gap-1 bg-slate-900/50 rounded-full overflow-hidden border border-slate-700/30">
            {data.complete > 0 && (
              <div
                className="bg-green-500 transition-all"
                style={{ width: `${completePercentage}%` }}
                title={`${data.complete} Complete`}
              ></div>
            )}
            {data.inProgress > 0 && (
              <div
                className="bg-yellow-500 transition-all"
                style={{ width: `${inProgressPercentage}%` }}
                title={`${data.inProgress} In Progress`}
              ></div>
            )}
            {data.notStarted > 0 && (
              <div
                className="bg-red-500 transition-all"
                style={{ width: `${notStartedPercentage}%` }}
                title={`${data.notStarted} Not Started`}
              ></div>
            )}
          </div>
          <div className="flex justify-between text-xs text-slate-500">
            <span>✅ {data.complete} Complete</span>
            <span>🟡 {data.inProgress} In Progress</span>
            <span>❌ {data.notStarted} Not Started</span>
          </div>
        </div>

        {/* Requirements Table */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-slate-300">Requirements</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.requirements.map((requirement) => (
              <div
                key={requirement.id}
                className={`border rounded-lg transition-all ${getStatusColor(requirement.status)}`}
              >
                {/* Header Row */}
                <div
                  className="p-4 cursor-pointer hover:bg-slate-900/50 transition-colors"
                  onClick={() => toggleRow(requirement.id)}
                >
                  <div className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 flex-1">
                      <ChevronDown
                        className={`w-5 h-5 text-slate-400 transition-transform ${
                          expandedRows[requirement.id] ? 'rotate-180' : ''
                        }`}
                      />
                      <div className="flex items-center gap-3 flex-1">
                        {getStatusIcon(requirement.status)}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{requirement.code}</p>
                          <p className="text-xs text-slate-400 truncate">{requirement.title}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {/* Completion % */}
                      <div className="text-right min-w-20">
                        <div className="text-sm font-bold text-white">{requirement.completionPercentage}%</div>
                        <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden w-12">
                          <div
                            className="h-full bg-blue-500 rounded-full transition-all"
                            style={{ width: `${requirement.completionPercentage}%` }}
                          ></div>
                        </div>
                      </div>
                      {/* Badge */}
                      <Badge variant={getStatusBadgeVariant(requirement.status)}>
                        {requirement.status}
                      </Badge>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-3 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
                      style={{ width: `${requirement.completionPercentage}%` }}
                    ></div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedRows[requirement.id] && (
                  <div className="border-t border-slate-700/30 p-4 bg-slate-900/20 space-y-3">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 mb-2">DESCRIPTION</h4>
                      <p className="text-sm text-slate-300">{requirement.description}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 mb-2">LAST UPDATED</h4>
                        <p className="text-sm text-white">
                          {new Date(requirement.lastUpdated).toLocaleDateString()}
                        </p>
                      </div>
                      {requirement.dueDate && (
                        <div>
                          <h4 className="text-xs font-semibold text-slate-400 mb-2">DUE DATE</h4>
                          <p className="text-sm text-white">
                            {new Date(requirement.dueDate).toLocaleDateString()}
                          </p>
                        </div>
                      )}
                    </div>

                    {requirement.evidence && requirement.evidence.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 mb-2">SUPPORTING EVIDENCE</h4>
                        <div className="flex flex-wrap gap-2">
                          {requirement.evidence.map((doc) => (
                            <button
                              key={doc}
                              className="flex items-center gap-1 px-3 py-1.5 bg-slate-700/50 hover:bg-slate-600/50 rounded text-xs text-cyan-400 transition-colors"
                            >
                              <FileText className="w-3.5 h-3.5" />
                              View Document
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                      >
                        <Info className="w-4 h-4 mr-1" />
                        View Details
                      </Button>
                      {requirement.status !== 'Complete' && (
                        <Button size="sm" variant="primary" className="flex-1">
                          Update Status
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-3 gap-4">
          <Card variant="default" className="bg-green-500/10 border-green-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-green-400 font-medium mb-1">COMPLETE</p>
                <p className="text-2xl font-bold text-green-400">{data.complete}</p>
                <p className="text-xs text-slate-400 mt-1">{completePercentage.toFixed(1)}% of total</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-yellow-500/10 border-yellow-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-yellow-400 font-medium mb-1">IN PROGRESS</p>
                <p className="text-2xl font-bold text-yellow-400">{data.inProgress}</p>
                <p className="text-xs text-slate-400 mt-1">{inProgressPercentage.toFixed(1)}% of total</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-red-500/10 border-red-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-red-400 font-medium mb-1">NOT STARTED</p>
                <p className="text-2xl font-bold text-red-400">{data.notStarted}</p>
                <p className="text-xs text-slate-400 mt-1">{notStartedPercentage.toFixed(1)}% of total</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </CardContent>
    </Card>
  )
}
