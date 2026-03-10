/**
 * ReportScheduler Component
 * Automated report scheduling with cron-style frequency selection
 */

import { useState } from 'react'
import { Calendar, Clock, Mail, Send, Trash2, Edit2, Play, Pause } from 'lucide-react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import { Badge } from './ui/Badge'
import { Dialog } from './ui/Dialog'
import { Toggle } from './ui/Toggle'
import type { ReportSchedule, ReportTemplate, CreateReportSchedule } from '../services/api'

interface ReportSchedulerProps {
  schedules: ReportSchedule[]
  templates: ReportTemplate[]
  onCreateSchedule: (data: CreateReportSchedule) => Promise<void>
  onUpdateSchedule: (id: string, data: Partial<ReportSchedule>) => Promise<void>
  onDeleteSchedule: (id: string) => Promise<void>
}

export function ReportScheduler({
  schedules,
  templates,
  onCreateSchedule,
  onUpdateSchedule,
  onDeleteSchedule,
}: ReportSchedulerProps) {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [editingSchedule, setEditingSchedule] = useState<ReportSchedule | null>(null)
  const [formData, setFormData] = useState<Partial<CreateReportSchedule>>({
    name: '',
    template_id: '',
    frequency: 'monthly',
    cron_expression: '0 0 1 * *',
    delivery_channels: [],
    enabled: true,
  })

  const frequencyOptions = [
    { value: 'daily', label: 'Daily', cron: '0 0 * * *' },
    { value: 'weekly', label: 'Weekly', cron: '0 0 * * 0' },
    { value: 'monthly', label: 'Monthly', cron: '0 0 1 * *' },
    { value: 'quarterly', label: 'Quarterly', cron: '0 0 1 */3 *' },
  ]

  const handleFrequencyChange = (frequency: string) => {
    const option = frequencyOptions.find((opt) => opt.value === frequency)
    setFormData({
      ...formData,
      frequency,
      cron_expression: option?.cron || '0 0 1 * *',
    })
  }

  const handleSubmit = async () => {
    if (!formData.name || !formData.template_id) return

    try {
      if (editingSchedule) {
        await onUpdateSchedule(editingSchedule.id, formData)
      } else {
        await onCreateSchedule(formData as CreateReportSchedule)
      }

      setIsCreateModalOpen(false)
      setEditingSchedule(null)
      setFormData({
        name: '',
        template_id: '',
        frequency: 'monthly',
        cron_expression: '0 0 1 * *',
        delivery_channels: [],
        enabled: true,
      })
    } catch (error) {
      console.error('Failed to save schedule:', error)
    }
  }

  const handleEdit = (schedule: ReportSchedule) => {
    setEditingSchedule(schedule)
    setFormData({
      name: schedule.name,
      template_id: schedule.template_id,
      frequency: schedule.frequency,
      cron_expression: schedule.cron_expression,
      delivery_channels: schedule.delivery_channels,
      enabled: schedule.enabled,
    })
    setIsCreateModalOpen(true)
  }

  const toggleSchedule = async (schedule: ReportSchedule) => {
    await onUpdateSchedule(schedule.id, { enabled: !schedule.enabled })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Report Schedules</h2>
          <p className="text-sm text-slate-400 mt-1">
            Automate report generation and delivery
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => setIsCreateModalOpen(true)}
          icon={<Calendar className="w-4 h-4" />}
        >
          New Schedule
        </Button>
      </div>

      {/* Schedules List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {schedules.map((schedule) => (
          <Card key={schedule.id} className="hover:border-blue-500/50 transition">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-1">{schedule.name}</h3>
                  <p className="text-sm text-slate-400">{schedule.template_name}</p>
                </div>
                <Badge variant={schedule.enabled ? 'success' : 'secondary'} size="sm">
                  {schedule.enabled ? 'Active' : 'Paused'}
                </Badge>
              </div>

              {/* Schedule Info */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <span className="text-slate-300">
                    {schedule.frequency.charAt(0).toUpperCase() + schedule.frequency.slice(1)}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="w-4 h-4 text-blue-400" />
                  <span className="text-slate-400">
                    Next run: {new Date(schedule.next_run).toLocaleString()}
                  </span>
                </div>

                {schedule.last_run && (
                  <div className="flex items-center gap-2 text-sm">
                    <Send className="w-4 h-4 text-green-400" />
                    <span className="text-slate-400">
                      Last run: {new Date(schedule.last_run).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>

              {/* Delivery Channels */}
              <div className="flex flex-wrap gap-2 mb-4">
                {schedule.delivery_channels.map((channel, index) => (
                  <Badge key={index} variant="info" size="sm">
                    {channel.type === 'email' && <Mail className="w-3 h-3 mr-1" />}
                    {channel.type}
                  </Badge>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-4 border-t border-slate-700/30">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleSchedule(schedule)}
                  icon={schedule.enabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                >
                  {schedule.enabled ? 'Pause' : 'Resume'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEdit(schedule)}
                  icon={<Edit2 className="w-4 h-4" />}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDeleteSchedule(schedule.id)}
                  icon={<Trash2 className="w-4 h-4" />}
                  className="text-red-400 hover:text-red-300"
                >
                  Delete
                </Button>
              </div>
            </div>
          </Card>
        ))}

        {schedules.length === 0 && (
          <div className="lg:col-span-2 text-center py-12 text-slate-500">
            <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No schedules configured yet</p>
            <p className="text-sm mt-1">Create your first automated report schedule</p>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      <Dialog
        open={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false)
          setEditingSchedule(null)
        }}
        title={editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}
      >
        <div className="space-y-4">
          <Input
            label="Schedule Name"
            placeholder="Monthly ESG Report"
            value={formData.name || ''}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Select
            label="Report Template"
            value={formData.template_id || ''}
            onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
            options={[
              { value: '', label: 'Select a template...' },
              ...templates.map((t) => ({ value: t.id, label: t.name })),
            ]}
            required
          />

          <Select
            label="Frequency"
            value={formData.frequency || 'monthly'}
            onChange={(e) => handleFrequencyChange(e.target.value)}
            options={frequencyOptions}
            required
          />

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Cron Expression
            </label>
            <Input
              value={formData.cron_expression || ''}
              onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
              placeholder="0 0 1 * *"
            />
            <p className="text-xs text-slate-500 mt-1">
              Advanced: Modify cron expression for custom scheduling
            </p>
          </div>

          <div className="flex items-center justify-between py-3 px-4 bg-slate-800/30 rounded-lg">
            <span className="text-sm text-slate-300">Enable Schedule</span>
            <Toggle
              checked={formData.enabled || false}
              onChange={(checked) => setFormData({ ...formData, enabled: checked })}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateModalOpen(false)
                setEditingSchedule(null)
              }}
              fullWidth
            >
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSubmit} fullWidth>
              {editingSchedule ? 'Save Changes' : 'Create Schedule'}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}
