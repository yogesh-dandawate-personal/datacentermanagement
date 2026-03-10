/**
 * AlertSettings Component
 * Configure notification preferences and quiet hours
 */

import { Mail, MessageSquare, Smartphone, Moon } from 'lucide-react'
import { Card } from './ui/Card'
import { Toggle } from './ui/Toggle'
import { Input } from './ui/Input'
import { Checkbox } from './ui/Checkbox'
import { Button } from './ui/Button'
import type { AlertSettings as AlertSettingsType } from '../services/api'

interface AlertSettingsProps {
  settings: AlertSettingsType
  onUpdate: (data: Partial<AlertSettingsType>) => Promise<void>
}

export function AlertSettings({ settings, onUpdate }: AlertSettingsProps) {
  const handleToggle = async (field: keyof AlertSettingsType, value: boolean) => {
    await onUpdate({ [field]: value })
  }

  const handleTextUpdate = async (field: keyof AlertSettingsType, value: string) => {
    await onUpdate({ [field]: value })
  }

  const handleQuietHoursToggle = async (enabled: boolean) => {
    await onUpdate({
      quiet_hours: { ...settings.quiet_hours, enabled },
    })
  }

  const handleSeverityFilter = async (severity: string, checked: boolean) => {
    const newFilters = checked
      ? [...settings.severity_filter, severity as any]
      : settings.severity_filter.filter((s) => s !== severity)

    await onUpdate({ severity_filter: newFilters })
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <h3 className="text-xl font-semibold text-white">Notification Channels</h3>
          <p className="text-sm text-slate-400 mt-1">Choose how you want to receive alerts</p>
        </div>

        <div className="p-6 space-y-6">
          {/* Email Notifications */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              <Mail className="w-5 h-5 text-cyan-400 mt-1" />
              <div className="flex-1">
                <p className="text-sm font-medium text-white">Email Notifications</p>
                <p className="text-xs text-slate-400 mt-1">Receive alerts via email</p>
                {settings.email_enabled && (
                  <Input
                    className="mt-3"
                    placeholder="email@company.com"
                    value={settings.email_address}
                    onChange={(e) => handleTextUpdate('email_address', e.target.value)}
                    onBlur={(e) => handleTextUpdate('email_address', e.target.value)}
                  />
                )}
              </div>
            </div>
            <Toggle
              checked={settings.email_enabled}
              onChange={(checked) => handleToggle('email_enabled', checked)}
            />
          </div>

          {/* Slack Notifications */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              <MessageSquare className="w-5 h-5 text-purple-400 mt-1" />
              <div className="flex-1">
                <p className="text-sm font-medium text-white">Slack Notifications</p>
                <p className="text-xs text-slate-400 mt-1">Send alerts to Slack channel</p>
                {settings.slack_enabled && (
                  <Input
                    className="mt-3"
                    placeholder="https://hooks.slack.com/..."
                    value={settings.slack_webhook_url || ''}
                    onChange={(e) => handleTextUpdate('slack_webhook_url', e.target.value)}
                    onBlur={(e) => handleTextUpdate('slack_webhook_url', e.target.value)}
                  />
                )}
              </div>
            </div>
            <Toggle
              checked={settings.slack_enabled}
              onChange={(checked) => handleToggle('slack_enabled', checked)}
            />
          </div>

          {/* Push Notifications */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <Smartphone className="w-5 h-5 text-green-400 mt-1" />
              <div>
                <p className="text-sm font-medium text-white">Push Notifications</p>
                <p className="text-xs text-slate-400 mt-1">Browser and mobile push</p>
              </div>
            </div>
            <Toggle
              checked={settings.push_enabled}
              onChange={(checked) => handleToggle('push_enabled', checked)}
            />
          </div>
        </div>
      </Card>

      {/* Quiet Hours */}
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Moon className="w-5 h-5 text-indigo-400" />
              <h3 className="text-xl font-semibold text-white">Quiet Hours</h3>
            </div>
            <Toggle
              checked={settings.quiet_hours.enabled}
              onChange={handleQuietHoursToggle}
            />
          </div>
        </div>

        {settings.quiet_hours.enabled && (
          <div className="p-6 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Start Time"
                type="time"
                value={settings.quiet_hours.start_time}
                onChange={(e) =>
                  onUpdate({
                    quiet_hours: { ...settings.quiet_hours, start_time: e.target.value },
                  })
                }
              />
              <Input
                label="End Time"
                type="time"
                value={settings.quiet_hours.end_time}
                onChange={(e) =>
                  onUpdate({
                    quiet_hours: { ...settings.quiet_hours, end_time: e.target.value },
                  })
                }
              />
            </div>

            <Input
              label="Timezone"
              placeholder="America/New_York"
              value={settings.quiet_hours.timezone}
              onChange={(e) =>
                onUpdate({
                  quiet_hours: { ...settings.quiet_hours, timezone: e.target.value },
                })
              }
            />

            <p className="text-xs text-slate-400">
              Non-critical alerts will be silenced during quiet hours
            </p>
          </div>
        )}
      </Card>

      {/* Severity Filter */}
      <Card>
        <div className="p-6 border-b border-slate-700/30">
          <h3 className="text-xl font-semibold text-white">Alert Severity Filter</h3>
          <p className="text-sm text-slate-400 mt-1">Choose which alert levels to receive</p>
        </div>

        <div className="p-6 space-y-3">
          {['critical', 'high', 'medium', 'low'].map((severity) => (
            <div key={severity} className="flex items-center gap-3">
              <Checkbox
                checked={settings.severity_filter.includes(severity as any)}
                onChange={(e) => handleSeverityFilter(severity, e.target.checked)}
              />
              <span className="text-sm text-slate-300 capitalize">{severity}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button variant="primary" onClick={() => onUpdate({})}>
          Save Settings
        </Button>
      </div>
    </div>
  )
}
