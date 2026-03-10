/**
 * Emissions Alerts Center
 * Manage active alerts, alert rules, and threshold configurations
 */

import { useState } from 'react'
import { Card, Button, Alert, Badge, Dialog, Spinner } from '@/components/ui'
import { useEmissionsAlerts } from '@/hooks/useEmissions'
import { AlertTriangle, Bell, Settings, Check, X, RefreshCw } from 'lucide-react'

export default function AlertsCenter() {
  const orgId = 'default-org' // Should come from user context
  const { alerts, loading, error, acknowledgeAlert, resolveAlert } = useEmissionsAlerts(orgId)

  const [filterSeverity, setFilterSeverity] = useState<string | undefined>()
  const [filterStatus, setFilterStatus] = useState<string | undefined>()
  const [showRuleDialog, setShowRuleDialog] = useState(false)

  // Filter alerts
  const filteredAlerts = (alerts || []).filter((alert) => {
    if (filterSeverity && alert.severity !== filterSeverity) return false
    if (filterStatus && alert.status !== filterStatus) return false
    return true
  })

  const severityConfig = {
    critical: { color: 'text-red-400', bg: 'bg-red-500/20', badge: 'danger' },
    warning: { color: 'text-orange-400', bg: 'bg-orange-500/20', badge: 'warning' },
    info: { color: 'text-blue-400', bg: 'bg-blue-500/20', badge: 'info' },
  }

  const statusConfig = {
    open: { color: 'text-red-400', label: 'Open' },
    acknowledged: { color: 'text-orange-400', label: 'Acknowledged' },
    resolved: { color: 'text-green-400', label: 'Resolved' },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Alerts Center</h1>
          <p className="text-slate-400 mt-1">Monitor and manage emissions threshold breaches</p>
        </div>

        <Button variant="primary" onClick={() => setShowRuleDialog(true)}>
          <Settings className="w-4 h-4" />
          Alert Rules
        </Button>
      </div>

      {error && (
        <Alert variant="error">
          <AlertTriangle className="w-5 h-5" />
          {error}
        </Alert>
      )}

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm text-slate-400">Total Alerts</p>
          <p className="text-3xl font-bold mt-2">{alerts?.length || 0}</p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Critical</p>
          <p className="text-3xl font-bold text-red-400 mt-2">
            {alerts?.filter((a) => a.severity === 'critical').length || 0}
          </p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Open</p>
          <p className="text-3xl font-bold text-orange-400 mt-2">
            {alerts?.filter((a) => a.status === 'open').length || 0}
          </p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Resolved</p>
          <p className="text-3xl font-bold text-green-400 mt-2">
            {alerts?.filter((a) => a.status === 'resolved').length || 0}
          </p>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap gap-3 items-center">
          <div>
            <label className="text-sm text-slate-400 mr-2">Filter by severity:</label>
            <select
              value={filterSeverity || ''}
              onChange={(e) => setFilterSeverity(e.target.value || undefined)}
              className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Severities</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mr-2">Filter by status:</label>
            <select
              value={filterStatus || ''}
              onChange={(e) => setFilterStatus(e.target.value || undefined)}
              className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-white focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Alerts List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : filteredAlerts.length > 0 ? (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => {
            const severityConfig_ = severityConfig[alert.severity as keyof typeof severityConfig]
            const statusConfig_ = statusConfig[alert.status as keyof typeof statusConfig]

            return (
              <Card
                key={alert.id}
                className={`border-l-4 ${severityConfig_?.bg || 'bg-slate-800/50'}`}
                style={{
                  borderLeftColor:
                    alert.severity === 'critical' ? '#ef4444' : alert.severity === 'warning' ? '#f97316' : '#3b82f6',
                }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <AlertTriangle className={`w-5 h-5 ${severityConfig_?.color}`} />
                      <h3 className="font-semibold">{alert.title}</h3>
                      <Badge variant={severityConfig_?.badge as any} className="text-xs">
                        {alert.severity}
                      </Badge>
                    </div>

                    <p className="text-sm text-slate-400 mb-3">{alert.alert_type}</p>

                    {alert.triggered_value && (
                      <p className="text-sm">
                        <span className="text-slate-400">Triggered Value: </span>
                        <span className="font-medium">{alert.triggered_value.toFixed(2)} tCO2e</span>
                      </p>
                    )}

                    <p className="text-xs text-slate-500 mt-2">
                      Triggered: {new Date(alert.triggered_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{statusConfig_?.label}</Badge>

                    {alert.status === 'open' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => acknowledgeAlert(alert.id)}
                      >
                        <Check className="w-4 h-4" />
                      </Button>
                    )}

                    {alert.status !== 'resolved' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => resolveAlert(alert.id)}
                      >
                        <Check className="w-4 h-4" />
                        Resolve
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      ) : (
        <Card>
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No alerts match your filters</p>
            <p className="text-sm text-slate-500 mt-1">Great job! No active threshold breaches detected.</p>
          </div>
        </Card>
      )}

      {/* Alert Rules Dialog */}
      {showRuleDialog && (
        <Dialog
          open={showRuleDialog}
          onOpenChange={setShowRuleDialog}
          title="Alert Rules"
        >
          <div className="space-y-4 max-h-96 overflow-y-auto">
            <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
              <h3 className="font-medium mb-2">Create New Alert Rule</h3>

              <div className="space-y-3">
                <div>
                  <label className="text-sm text-slate-400 block mb-1">Rule Name</label>
                  <input
                    type="text"
                    placeholder="e.g., High emissions alert"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Metric</label>
                    <select className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:border-blue-500 focus:outline-none">
                      <option>total_emissions</option>
                      <option>scope_1</option>
                      <option>scope_2</option>
                      <option>scope_3</option>
                      <option>carbon_intensity</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Operator</label>
                    <select className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:border-blue-500 focus:outline-none">
                      <option>&gt;</option>
                      <option>&lt;</option>
                      <option>&gt;=</option>
                      <option>&lt;=</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Threshold</label>
                    <input
                      type="number"
                      placeholder="100000"
                      className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-sm text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm text-slate-400 block mb-1">Severity</label>
                  <select className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-sm text-white focus:border-blue-500 focus:outline-none">
                    <option value="critical">Critical</option>
                    <option value="warning">Warning</option>
                    <option value="info">Info</option>
                  </select>
                </div>

                <Button variant="primary" className="w-full">
                  Create Rule
                </Button>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-2">Active Rules</h3>
              <div className="space-y-2">
                {[
                  { name: 'High emissions warning', metric: 'total_emissions', threshold: '100000 tCO2e', severity: 'warning' },
                  { name: 'Critical carbon intensity', metric: 'carbon_intensity', threshold: '500 g/kWh', severity: 'critical' },
                ].map((rule, idx) => (
                  <div key={idx} className="p-3 bg-slate-900 rounded border border-slate-700 text-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{rule.name}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          {rule.metric} &gt; {rule.threshold}
                        </p>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {rule.severity}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  )
}
