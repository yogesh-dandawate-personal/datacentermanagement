/**
 * AlertConfig Component
 * Configure alert rules and thresholds
 */

import { useState } from 'react'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { Card } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import { Toggle } from './ui/Toggle'
import { Badge } from './ui/Badge'
import { Dialog } from './ui/Dialog'
import { Checkbox } from './ui/Checkbox'
import type { AlertRule, CreateAlertRule } from '../services/api'

interface AlertConfigProps {
  rules: AlertRule[]
  onCreate: (data: CreateAlertRule) => Promise<void>
  onUpdate: (id: string, data: Partial<AlertRule>) => Promise<void>
  onDelete: (id: string) => Promise<void>
}

export function AlertConfig({ rules, onCreate, onUpdate, onDelete }: AlertConfigProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<AlertRule | null>(null)
  const [formData, setFormData] = useState<Partial<CreateAlertRule>>({
    name: '',
    metric: '',
    condition: 'greater_than',
    threshold: 0,
    severity: 'medium',
    enabled: true,
    facility_ids: [],
    notification_channels: ['email'],
  })

  const handleSubmit = async () => {
    if (!formData.name || !formData.metric) return

    try {
      if (editing) {
        await onUpdate(editing.id, formData as Partial<AlertRule>)
      } else {
        await onCreate(formData as CreateAlertRule)
      }
      closeModal()
    } catch (error) {
      console.error('Failed to save rule:', error)
    }
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditing(null)
    setFormData({
      name: '',
      metric: '',
      condition: 'greater_than',
      threshold: 0,
      severity: 'medium',
      enabled: true,
      facility_ids: [],
      notification_channels: ['email'],
    })
  }

  const handleEdit = (rule: AlertRule) => {
    setEditing(rule)
    setFormData({
      name: rule.name,
      metric: rule.metric,
      condition: rule.condition,
      threshold: rule.threshold,
      severity: rule.severity,
      enabled: rule.enabled,
      facility_ids: rule.facility_ids,
      notification_channels: rule.notification_channels,
    })
    setIsModalOpen(true)
  }

  const toggleRule = async (rule: AlertRule) => {
    await onUpdate(rule.id, { enabled: !rule.enabled })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold text-white">Alert Rules</h3>
          <p className="text-sm text-slate-400 mt-1">Configure custom alert thresholds and conditions</p>
        </div>
        <Button variant="primary" onClick={() => setIsModalOpen(true)} icon={<Plus className="w-4 h-4" />}>
          New Rule
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {rules.map((rule) => (
          <Card key={rule.id} className="hover:border-blue-500/50 transition">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h4 className="text-lg font-semibold text-white mb-1">{rule.name}</h4>
                  <p className="text-sm text-slate-400">
                    {rule.metric} {rule.condition.replace('_', ' ')} {rule.threshold}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={rule.enabled ? 'success' : 'secondary'} size="sm">
                    {rule.enabled ? 'Active' : 'Paused'}
                  </Badge>
                  <Badge
                    variant={
                      rule.severity === 'critical'
                        ? 'danger'
                        : rule.severity === 'high'
                        ? 'warning'
                        : 'info'
                    }
                    size="sm"
                  >
                    {rule.severity}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex flex-wrap gap-2">
                  {rule.notification_channels.map((channel) => (
                    <Badge key={channel} variant="info" size="sm">{channel}</Badge>
                  ))}
                </div>
                {rule.facility_ids.length > 0 && (
                  <p className="text-xs text-slate-500">
                    Applies to {rule.facility_ids.length} facilities
                  </p>
                )}
              </div>

              <div className="flex gap-2 pt-4 border-t border-slate-700/30">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleRule(rule)}
                >
                  {rule.enabled ? 'Pause' : 'Resume'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEdit(rule)}
                  icon={<Edit2 className="w-4 h-4" />}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(rule.id)}
                  icon={<Trash2 className="w-4 h-4" />}
                  className="text-red-400"
                >
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={isModalOpen} onClose={closeModal} title={editing ? 'Edit Rule' : 'Create Alert Rule'}>
        <div className="space-y-4">
          <Input
            label="Rule Name"
            placeholder="High Energy Usage Alert"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Select
            label="Metric"
            value={formData.metric || ''}
            onChange={(e) => setFormData({ ...formData, metric: e.target.value })}
            options={[
              { value: '', label: 'Select metric...' },
              { value: 'energy_usage', label: 'Energy Usage (kW)' },
              { value: 'emissions', label: 'Emissions (tCO₂e)' },
              { value: 'renewable_percentage', label: 'Renewable %' },
              { value: 'pue', label: 'PUE' },
              { value: 'temperature', label: 'Temperature (°C)' },
            ]}
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Condition"
              value={formData.condition || 'greater_than'}
              onChange={(e) => setFormData({ ...formData, condition: e.target.value as any })}
              options={[
                { value: 'greater_than', label: 'Greater than' },
                { value: 'less_than', label: 'Less than' },
                { value: 'equals', label: 'Equals' },
                { value: 'change_percentage', label: 'Change %' },
              ]}
              required
            />

            <Input
              label="Threshold"
              type="number"
              placeholder="1000"
              value={formData.threshold || 0}
              onChange={(e) => setFormData({ ...formData, threshold: parseFloat(e.target.value) })}
              required
            />
          </div>

          <Select
            label="Severity"
            value={formData.severity || 'medium'}
            onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
            options={[
              { value: 'critical', label: 'Critical' },
              { value: 'high', label: 'High' },
              { value: 'medium', label: 'Medium' },
              { value: 'low', label: 'Low' },
            ]}
            required
          />

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Notification Channels</label>
            <div className="space-y-2">
              {['email', 'slack', 'push'].map((channel) => (
                <div key={channel} className="flex items-center gap-3">
                  <Checkbox
                    checked={(formData.notification_channels || []).includes(channel as any)}
                    onChange={(checked) => {
                      const channels = formData.notification_channels || []
                      const newChannels = checked
                        ? [...channels, channel as any]
                        : channels.filter((c) => c !== channel)
                      setFormData({ ...formData, notification_channels: newChannels })
                    }}
                  />
                  <span className="text-sm text-slate-300 capitalize">{channel}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between py-3 px-4 bg-slate-800/30 rounded-lg">
            <span className="text-sm text-slate-300">Enable Rule</span>
            <Toggle
              checked={formData.enabled || false}
              onChange={(checked) => setFormData({ ...formData, enabled: checked })}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="outline" onClick={closeModal} fullWidth>Cancel</Button>
            <Button variant="primary" onClick={handleSubmit} fullWidth>
              {editing ? 'Save Changes' : 'Create Rule'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}
