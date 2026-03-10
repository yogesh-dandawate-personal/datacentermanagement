/**
 * Alerts Dashboard Page
 * Real-time alerts, notification settings, alert history, and rule configuration
 */

import { useState } from 'react'
import { Bell, Settings, History, Sliders } from 'lucide-react'
import { useAlerts } from '../hooks/useAlerts'
import { AlertSettings } from '../components/AlertSettings'
import { AlertHistory } from '../components/AlertHistory'
import { AlertConfig } from '../components/AlertConfig'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { Alert } from '../components/ui/Alert'

export function Alerts() {
  const [activeTab, setActiveTab] = useState<'alerts' | 'settings' | 'history' | 'config'>('alerts')

  const {
    alerts,
    alertHistory,
    settings,
    rules,
    loading,
    error,
    dismissAlert,
    snoozeAlert,
    updateSettings,
    createRule,
    updateRule,
    deleteRule,
    refetch,
  } = useAlerts('active')

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
        <span className="ml-3 text-slate-400">Loading alerts...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert
          variant="error"
          title="Error Loading Alerts"
          message={error}
          action={<Button size="sm" variant="outline" onClick={() => refetch()}>Retry</Button>}
        />
      </div>
    )
  }

  const tabs = [
    { id: 'alerts', label: 'Active Alerts', icon: Bell, count: alerts.length },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'history', label: 'History', icon: History },
    { id: 'config', label: 'Rules', icon: Sliders, count: rules.length },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
          <Bell className="w-8 h-8 text-cyan-400" />
          Alert Management
        </h1>
        <p className="text-slate-400 mt-1">
          Monitor real-time alerts and configure notification preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-700/50 pb-4">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                activeTab === tab.id
                  ? 'bg-blue-600/20 border border-blue-500/50 text-white'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
              {tab.count !== undefined && (
                <Badge variant={activeTab === tab.id ? 'primary' : 'secondary'} size="sm">
                  {tab.count}
                </Badge>
              )}
            </button>
          )
        })}
      </div>

      {/* Content */}
      {activeTab === 'alerts' && (
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <Card>
              <div className="p-12 text-center text-slate-500">
                <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>No active alerts</p>
                <p className="text-sm mt-1">All systems operating normally</p>
              </div>
            </Card>
          ) : (
            alerts.map((alert) => {
              const getSeverityColor = (severity: string) => {
                switch (severity) {
                  case 'critical':
                    return 'border-red-500/50 bg-red-500/10'
                  case 'high':
                    return 'border-orange-500/50 bg-orange-500/10'
                  case 'medium':
                    return 'border-yellow-500/50 bg-yellow-500/10'
                  case 'low':
                    return 'border-blue-500/50 bg-blue-500/10'
                  default:
                    return 'border-slate-500/50'
                }
              }

              return (
                <Card key={alert.id} className={getSeverityColor(alert.severity)}>
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold text-white">{alert.title}</h3>
                          <Badge
                            variant={
                              alert.severity === 'critical'
                                ? 'danger'
                                : alert.severity === 'high'
                                ? 'warning'
                                : 'info'
                            }
                            size="sm"
                          >
                            {alert.severity}
                          </Badge>
                          <Badge variant="secondary" size="sm">{alert.type}</Badge>
                        </div>
                        <p className="text-sm text-slate-300">{alert.message}</p>
                        {alert.metric && (
                          <div className="mt-2 text-sm">
                            <span className="text-slate-400">Metric: </span>
                            <span className="text-slate-300 font-medium">{alert.metric}</span>
                            {alert.current_value && (
                              <>
                                <span className="text-slate-400 mx-2">|</span>
                                <span className="text-cyan-400 font-semibold">
                                  {alert.current_value}
                                </span>
                                {alert.threshold_value && (
                                  <span className="text-slate-500">
                                    {' '}
                                    / {alert.threshold_value} threshold
                                  </span>
                                )}
                              </>
                            )}
                          </div>
                        )}
                        <p className="text-xs text-slate-500 mt-2">
                          {new Date(alert.timestamp).toLocaleString()}
                          {alert.facility_name && ` • ${alert.facility_name}`}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2 pt-4 border-t border-slate-700/30">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => snoozeAlert(alert.id, 60)}
                      >
                        Snooze 1h
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => snoozeAlert(alert.id, 1440)}
                      >
                        Snooze 24h
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => dismissAlert(alert.id)}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </Card>
              )
            })
          )}
        </div>
      )}

      {activeTab === 'settings' && settings && (
        <AlertSettings settings={settings} onUpdate={updateSettings} />
      )}

      {activeTab === 'history' && (
        <AlertHistory alerts={alertHistory} />
      )}

      {activeTab === 'config' && (
        <AlertConfig
          rules={rules}
          onCreate={async (data) => { await createRule(data); }}
          onUpdate={updateRule}
          onDelete={deleteRule}
        />
      )}
    </div>
  )
}
