/**
 * Compliance Dashboard Page
 * Main page for monitoring GRI/TCFD/CDP compliance status
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Spinner, Alert } from '../components/ui'
import { ComplianceScore as ComplianceScoreComponent } from '../components/ComplianceScore'
import { ComplianceMatrix } from '../components/ComplianceMatrix'
import { GapAnalysis } from '../components/GapAnalysis'
import { RemediationTasks } from '../components/RemediationTasks'
import { TargetTracking } from '../components/TargetTracking'
import {
  useComplianceStatus,
  useComplianceScore,
  useComplianceMatrix,
  useComplianceGaps,
  useRemediationTasks,
  useTargetTracking,
  useKPITargets,
  useAuditTrail,
} from '../hooks/useCompliance'
import { Download, FileText, Clock, AlertTriangle, CheckCircle2, TrendingUp } from 'lucide-react'

type TabType = 'overview' | 'gri' | 'tcfd' | 'cdp' | 'gaps' | 'tasks' | 'targets' | 'audit'

export function Compliance() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [isExporting, setIsExporting] = useState(false)

  // Fetch all compliance data
  const complianceStatus = useComplianceStatus()
  const complianceScore = useComplianceScore()
  const griMatrix = useComplianceMatrix('GRI')
  const tcfdMatrix = useComplianceMatrix('TCFD')
  const cdpMatrix = useComplianceMatrix('CDP')
  const gaps = useComplianceGaps()
  const tasks = useRemediationTasks()
  const targetTracking = useTargetTracking()
  const kpiTargets = useKPITargets()
  const auditTrail = useAuditTrail()

  const isLoading =
    complianceStatus.loading ||
    complianceScore.loading ||
    griMatrix.loading ||
    tcfdMatrix.loading ||
    cdpMatrix.loading ||
    gaps.loading ||
    tasks.loading ||
    targetTracking.loading ||
    kpiTargets.loading ||
    auditTrail.loading

  // Handle export
  const handleExportReport = async () => {
    setIsExporting(true)
    try {
      // Simulate report generation
      await new Promise((resolve) => setTimeout(resolve, 2000))
      alert('Report exported successfully!')
    } catch (error) {
      alert('Failed to export report')
    } finally {
      setIsExporting(false)
    }
  }

  // Get status color
  const getStatusColor = (status: string) => {
    if (status === 'On Track') return 'bg-green-500/10 border-green-500/20 text-green-400'
    if (status === 'At Risk') return 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400'
    return 'bg-red-500/10 border-red-500/20 text-red-400'
  }

  const getStatusIcon = (status: string) => {
    if (status === 'On Track') return <CheckCircle2 className="w-5 h-5" />
    if (status === 'At Risk') return <AlertTriangle className="w-5 h-5" />
    return <AlertTriangle className="w-5 h-5" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="mb-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Compliance Dashboard</h1>
            <p className="text-slate-400">Monitor GRI, TCFD, and CDP compliance requirements</p>
          </div>
          <Button
            size="lg"
            variant="primary"
            className="flex items-center gap-2 w-full md:w-auto"
            onClick={handleExportReport}
            disabled={isLoading || isExporting}
          >
            {isExporting ? (
              <>
                <Spinner size="sm" />
                Generating Report...
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                Export Report
              </>
            )}
          </Button>
        </div>
      </section>

      {/* Status Overview */}
      {complianceStatus.data && (
        <section>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 sm:gap-6">
            {/* Overall Status */}
            <Card className={`border ${getStatusColor(complianceStatus.data.overallStatus)}`}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-400 mb-1">OVERALL STATUS</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.overallStatus}</p>
                  </div>
                  {getStatusIcon(complianceStatus.data.overallStatus)}
                </div>
                <p className="text-sm text-slate-400">
                  <span className="text-lg font-bold text-white">{complianceStatus.data.scorePercentage}%</span> complete
                </p>
              </CardContent>
            </Card>

            {/* Compliance Score */}
            <Card className="border-blue-500/20 bg-blue-500/10">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-400 mb-1">COMPLIANCE SCORE</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.scorePercentage}</p>
                  </div>
                  <TrendingUp className="w-5 h-5 text-blue-400" />
                </div>
                <p className="text-sm text-slate-400">
                  <span className="font-bold text-blue-400">
                    {complianceStatus.data.submittedMetricsCount}/{complianceStatus.data.requiredMetricsCount}
                  </span>{' '}
                  metrics submitted
                </p>
              </CardContent>
            </Card>

            {/* Gaps Identified */}
            <Card className="border-red-500/20 bg-red-500/10">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-400 mb-1">GAPS IDENTIFIED</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.gapCount}</p>
                  </div>
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                </div>
                <p className="text-sm text-slate-400">
                  <span className="font-bold text-red-400">{complianceStatus.data.criticalGapCount}</span> critical gaps
                </p>
              </CardContent>
            </Card>

            {/* Pending Tasks */}
            <Card className="border-yellow-500/20 bg-yellow-500/10">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-xs font-semibold text-slate-400 mb-1">PENDING TASKS</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.pendingTasksCount}</p>
                  </div>
                  <Clock className="w-5 h-5 text-yellow-400" />
                </div>
                <p className="text-sm text-slate-400">
                  <span className="font-bold text-red-400">{complianceStatus.data.overdueTasks}</span> overdue
                </p>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Framework Status Cards */}
      {complianceStatus.data && (
        <section>
          <h2 className="text-lg font-bold text-white mb-4">Framework Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* GRI */}
            <Card
              className={`border cursor-pointer hover:border-blue-500/50 transition-colors ${getStatusColor(complianceStatus.data.frameworks.gri.status)}`}
              onClick={() => setActiveTab('gri')}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">GRI Standards</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.frameworks.gri.score}%</p>
                  </div>
                  <Badge variant="info">{complianceStatus.data.frameworks.gri.status}</Badge>
                </div>
                <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full"
                    style={{ width: `${complianceStatus.data.frameworks.gri.score}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            {/* TCFD */}
            <Card
              className={`border cursor-pointer hover:border-cyan-500/50 transition-colors ${getStatusColor(complianceStatus.data.frameworks.tcfd.status)}`}
              onClick={() => setActiveTab('tcfd')}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">TCFD Framework</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.frameworks.tcfd.score}%</p>
                  </div>
                  <Badge variant="warning">{complianceStatus.data.frameworks.tcfd.status}</Badge>
                </div>
                <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 rounded-full"
                    style={{ width: `${complianceStatus.data.frameworks.tcfd.score}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            {/* CDP */}
            <Card
              className={`border cursor-pointer hover:border-green-500/50 transition-colors ${getStatusColor(complianceStatus.data.frameworks.cdp.status)}`}
              onClick={() => setActiveTab('cdp')}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-400 mb-1">CDP Disclosure</p>
                    <p className="text-2xl font-bold text-white">{complianceStatus.data.frameworks.cdp.score}%</p>
                  </div>
                  <Badge variant="warning">{complianceStatus.data.frameworks.cdp.status}</Badge>
                </div>
                <div className="h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${complianceStatus.data.frameworks.cdp.score}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Tabs */}
      <section className="border-b border-slate-700/30 -mx-6 px-6">
        <div className="flex gap-1 overflow-x-auto">
          {[
            { id: 'overview' as TabType, label: 'Overview', icon: '📊' },
            { id: 'gri' as TabType, label: 'GRI', icon: '📋' },
            { id: 'tcfd' as TabType, label: 'TCFD', icon: '🌡️' },
            { id: 'cdp' as TabType, label: 'CDP', icon: '💧' },
            { id: 'gaps' as TabType, label: 'Gaps', icon: '⚠️' },
            { id: 'tasks' as TabType, label: 'Tasks', icon: '✓' },
            { id: 'targets' as TabType, label: 'Targets', icon: '🎯' },
            { id: 'audit' as TabType, label: 'Audit Trail', icon: '📜' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 border-b-2 transition-colors text-sm font-medium whitespace-nowrap ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-300'
                  : 'border-transparent text-slate-400 hover:text-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </section>

      {/* Tab Content */}
      <section>
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <ComplianceScoreComponent
              data={complianceScore.data}
              loading={complianceScore.loading}
            />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <GapAnalysis gaps={gaps.data} loading={gaps.loading} />
              <RemediationTasks tasks={tasks.data} loading={tasks.loading} />
            </div>
          </div>
        )}

        {activeTab === 'gri' && (
          <ComplianceMatrix
            data={griMatrix.data}
            loading={griMatrix.loading}
            framework="GRI"
          />
        )}

        {activeTab === 'tcfd' && (
          <ComplianceMatrix
            data={tcfdMatrix.data}
            loading={tcfdMatrix.loading}
            framework="TCFD"
          />
        )}

        {activeTab === 'cdp' && (
          <ComplianceMatrix
            data={cdpMatrix.data}
            loading={cdpMatrix.loading}
            framework="CDP"
          />
        )}

        {activeTab === 'gaps' && (
          <GapAnalysis gaps={gaps.data} loading={gaps.loading} />
        )}

        {activeTab === 'tasks' && (
          <RemediationTasks tasks={tasks.data} loading={tasks.loading} />
        )}

        {activeTab === 'targets' && (
          <TargetTracking
            targets={targetTracking.data}
            kpiTargets={kpiTargets.data}
            loading={targetTracking.loading || kpiTargets.loading}
          />
        )}

        {activeTab === 'audit' && (
          <Card>
            <CardHeader>
              <CardTitle>Audit Trail</CardTitle>
              <CardDescription>Timeline of compliance status changes</CardDescription>
            </CardHeader>
            <CardContent>
              {auditTrail.loading ? (
                <div className="flex justify-center py-8">
                  <Spinner />
                </div>
              ) : auditTrail.data && auditTrail.data.length > 0 ? (
                <div className="space-y-4">
                  {auditTrail.data.map((entry, i) => (
                    <div key={entry.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className="w-3 h-3 rounded-full bg-blue-500 mt-1.5"></div>
                        {i !== auditTrail.data!.length - 1 && (
                          <div className="w-0.5 h-12 bg-slate-700/30 my-2"></div>
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <p className="text-sm font-medium text-white">{entry.description}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          {new Date(entry.timestamp).toLocaleDateString()} at{' '}
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">By {entry.changedBy}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">No audit entries found</div>
              )}
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  )
}
