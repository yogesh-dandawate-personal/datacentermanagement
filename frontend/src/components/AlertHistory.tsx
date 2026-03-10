/**
 * AlertHistory Component
 * View past alerts with filtering and search
 */

import { useState } from 'react'
import { History, Filter } from 'lucide-react'
import { Card } from './ui/Card'
import { Badge } from './ui/Badge'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import type { AlertItem } from '../services/api'

interface AlertHistoryProps {
  alerts: AlertItem[]
}

export function AlertHistory({ alerts }: AlertHistoryProps) {
  const [search, setSearch] = useState('')
  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      alert.title.toLowerCase().includes(search.toLowerCase()) ||
      alert.message.toLowerCase().includes(search.toLowerCase())

    const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter
    const matchesType = typeFilter === 'all' || alert.type === typeFilter

    return matchesSearch && matchesSeverity && matchesType
  })

  if (alerts.length === 0) {
    return (
      <Card>
        <div className="p-12 text-center text-slate-500">
          <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No alert history available</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <Input
              placeholder="Search alerts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <Select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            options={[
              { value: 'all', label: 'All Severities' },
              { value: 'critical', label: 'Critical' },
              { value: 'high', label: 'High' },
              { value: 'medium', label: 'Medium' },
              { value: 'low', label: 'Low' },
            ]}
          />

          <Select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            options={[
              { value: 'all', label: 'All Types' },
              { value: 'threshold', label: 'Threshold' },
              { value: 'anomaly', label: 'Anomaly' },
              { value: 'compliance', label: 'Compliance' },
              { value: 'system', label: 'System' },
            ]}
          />
        </div>
      </Card>

      {/* Alert List */}
      <div className="space-y-3">
        {filteredAlerts.map((alert) => (
          <Card key={alert.id} className="p-4 hover:bg-slate-800/30 transition">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
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
                  <Badge
                    variant={
                      alert.status === 'dismissed'
                        ? 'secondary'
                        : alert.status === 'snoozed'
                        ? 'warning'
                        : 'info'
                    }
                    size="sm"
                  >
                    {alert.status}
                  </Badge>
                </div>

                <h4 className="text-sm font-semibold text-white mb-1">{alert.title}</h4>
                <p className="text-sm text-slate-400">{alert.message}</p>

                <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                  <span>{new Date(alert.timestamp).toLocaleString()}</span>
                  {alert.facility_name && <span>• {alert.facility_name}</span>}
                  {alert.metric && <span>• {alert.metric}</span>}
                </div>
              </div>
            </div>
          </Card>
        ))}

        {filteredAlerts.length === 0 && (
          <Card>
            <div className="p-8 text-center text-slate-500">
              <Filter className="w-8 h-8 mx-auto mb-2 opacity-30" />
              <p>No alerts match your filters</p>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
