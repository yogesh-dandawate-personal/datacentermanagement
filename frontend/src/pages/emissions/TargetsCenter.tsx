/**
 * Emissions Reduction Targets Center
 * Track and manage emissions reduction goals
 */

import { useState } from 'react'
import { Card, Button, Dialog, Badge, Spinner, Alert } from '@/components/ui'
import { useEmissionsTargets } from '@/hooks/useEmissions'
import { Target, Plus, TrendingDown, AlertCircle } from 'lucide-react'

export default function TargetsCenter() {
  const orgId = 'default-org'
  const { targets, loading, error, createTarget } = useEmissionsTargets(orgId)
  const [showDialog, setShowDialog] = useState(false)

  const statusConfig = {
    on_track: { color: 'text-green-400', bg: 'bg-green-500/20', badge: 'success' },
    at_risk: { color: 'text-orange-400', bg: 'bg-orange-500/20', badge: 'warning' },
    failed: { color: 'text-red-400', bg: 'bg-red-500/20', badge: 'danger' },
    achieved: { color: 'text-blue-400', bg: 'bg-blue-500/20', badge: 'info' },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reduction Targets</h1>
          <p className="text-slate-400 mt-1">Track progress toward emissions reduction goals</p>
        </div>

        <Button variant="primary" onClick={() => setShowDialog(true)}>
          <Plus className="w-4 h-4" />
          New Target
        </Button>
      </div>

      {error && (
        <Alert variant="error">
          <AlertCircle className="w-5 h-5" />
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <p className="text-sm text-slate-400">Total Targets</p>
          <p className="text-3xl font-bold mt-2">{targets?.length || 0}</p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">On Track</p>
          <p className="text-3xl font-bold text-green-400 mt-2">
            {targets?.filter((t) => t.status === 'on_track').length || 0}
          </p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">At Risk</p>
          <p className="text-3xl font-bold text-orange-400 mt-2">
            {targets?.filter((t) => t.status === 'at_risk').length || 0}
          </p>
        </Card>
      </div>

      {/* Targets List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : targets && targets.length > 0 ? (
        <div className="space-y-4">
          {targets.map((target) => {
            const statusConfig_ = statusConfig[target.status as keyof typeof statusConfig]
            const progress = target.progress_percentage || 0
            const yearsRemaining = target.target_year - new Date().getFullYear()

            return (
              <Card key={target.id} className={`border-l-4 ${statusConfig_?.bg || ''}`}>
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{target.target_name}</h3>
                    <p className="text-sm text-slate-400 mt-1">Target Year: {target.target_year}</p>
                  </div>

                  <Badge variant={statusConfig_?.badge as any} className="text-xs">
                    {target.status}
                  </Badge>
                </div>

                {/* Progress Bar */}
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-400">Progress</span>
                    <span className="text-sm font-medium">{progress.toFixed(0)}%</span>
                  </div>

                  <div className="w-full bg-slate-700 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${
                        target.status === 'on_track'
                          ? 'bg-green-500'
                          : target.status === 'at_risk'
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="bg-slate-800/50 p-3 rounded">
                    <p className="text-xs text-slate-400">Baseline</p>
                    <p className="text-lg font-medium mt-1">{target.baseline_value.toFixed(0)}</p>
                    <p className="text-xs text-slate-500">tCO2e</p>
                  </div>

                  <div className="bg-slate-800/50 p-3 rounded">
                    <p className="text-xs text-slate-400">Target</p>
                    <p className="text-lg font-medium mt-1">{target.target_value.toFixed(0)}</p>
                    <p className="text-xs text-slate-500">tCO2e</p>
                  </div>
                </div>

                {/* Status Message */}
                {yearsRemaining > 0 && (
                  <p className="text-xs text-slate-400">
                    {yearsRemaining} year{yearsRemaining > 1 ? 's' : ''} remaining
                  </p>
                )}

                {yearsRemaining === 0 && (
                  <p className="text-xs text-orange-400">This year is your target year</p>
                )}

                {yearsRemaining < 0 && (
                  <p className="text-xs text-red-400">Target year has passed</p>
                )}
              </Card>
            )
          })}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <Target className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No targets set yet</p>
            <p className="text-sm text-slate-500 mt-1">Create your first emissions reduction target</p>
            <Button variant="primary" onClick={() => setShowDialog(true)} className="mt-4">
              Create Target
            </Button>
          </div>
        </Card>
      )}

      {/* Create Target Dialog */}
      {showDialog && (
        <Dialog
          open={showDialog}
          onOpenChange={setShowDialog}
          title="Create Emissions Reduction Target"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Target Name</label>
              <input
                type="text"
                placeholder="e.g., Net-zero by 2030"
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Target Type</label>
              <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none">
                <option value="absolute_reduction">Absolute Reduction</option>
                <option value="intensity_reduction">Intensity Reduction</option>
                <option value="net_zero">Net Zero</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Baseline Year</label>
                <input
                  type="number"
                  placeholder="2021"
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Target Year</label>
                <input
                  type="number"
                  placeholder="2030"
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Baseline Value (tCO2e)</label>
                <input
                  type="number"
                  placeholder="50000"
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Target Value (tCO2e)</label>
                <input
                  type="number"
                  placeholder="0"
                  className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button variant="primary" className="flex-1">
                Create Target
              </Button>
              <Button variant="outline" onClick={() => setShowDialog(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  )
}
