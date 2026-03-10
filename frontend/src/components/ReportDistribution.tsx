/**
 * ReportDistribution Component
 * Configure delivery channels (email, Slack, webhook)
 */

import { useState } from 'react'
import { Mail, MessageSquare, Webhook, Plus, Trash2 } from 'lucide-react'
import { Card } from './ui/Card'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select } from './ui/Select'
import { Badge } from './ui/Badge'

interface DeliveryChannel {
  type: 'email' | 'slack' | 'webhook'
  config: Record<string, any>
}

interface ReportDistributionProps {
  channels: DeliveryChannel[]
  onChange: (channels: DeliveryChannel[]) => void
}

export function ReportDistribution({ channels, onChange }: ReportDistributionProps) {
  const [newChannel, setNewChannel] = useState<Partial<DeliveryChannel>>({
    type: 'email',
    config: {},
  })

  const addChannel = () => {
    if (!newChannel.type) return
    onChange([...channels, newChannel as DeliveryChannel])
    setNewChannel({ type: 'email', config: {} })
  }

  const removeChannel = (index: number) => {
    onChange(channels.filter((_, i) => i !== index))
  }

  const updateConfig = (key: string, value: string) => {
    setNewChannel({
      ...newChannel,
      config: { ...newChannel.config, [key]: value },
    })
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-white">Delivery Channels</h3>

      {/* Existing Channels */}
      <div className="space-y-3">
        {channels.map((channel, index) => (
          <Card key={index} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {channel.type === 'email' && <Mail className="w-5 h-5 text-cyan-400" />}
                {channel.type === 'slack' && <MessageSquare className="w-5 h-5 text-purple-400" />}
                {channel.type === 'webhook' && <Webhook className="w-5 h-5 text-green-400" />}
                <div>
                  <Badge variant="info" size="sm">{channel.type}</Badge>
                  <p className="text-sm text-slate-300 mt-1">
                    {channel.type === 'email' && channel.config.recipients}
                    {channel.type === 'slack' && channel.config.channel}
                    {channel.type === 'webhook' && channel.config.url}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeChannel(index)}
                icon={<Trash2 className="w-4 h-4" />}
                className="text-red-400"
              >
                Remove
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Add New Channel */}
      <Card className="p-4">
        <h4 className="text-sm font-semibold text-white mb-3">Add Delivery Channel</h4>
        <div className="space-y-3">
          <Select
            label="Channel Type"
            value={newChannel.type || 'email'}
            onChange={(e) => setNewChannel({ ...newChannel, type: e.target.value as any })}
            options={[
              { value: 'email', label: 'Email' },
              { value: 'slack', label: 'Slack' },
              { value: 'webhook', label: 'Webhook' },
            ]}
          />

          {newChannel.type === 'email' && (
            <Input
              label="Email Recipients"
              placeholder="user@company.com, team@company.com"
              value={newChannel.config?.recipients || ''}
              onChange={(e) => updateConfig('recipients', e.target.value)}
            />
          )}

          {newChannel.type === 'slack' && (
            <>
              <Input
                label="Slack Channel"
                placeholder="#esg-reports"
                value={newChannel.config?.channel || ''}
                onChange={(e) => updateConfig('channel', e.target.value)}
              />
              <Input
                label="Webhook URL"
                placeholder="https://hooks.slack.com/..."
                value={newChannel.config?.webhook_url || ''}
                onChange={(e) => updateConfig('webhook_url', e.target.value)}
              />
            </>
          )}

          {newChannel.type === 'webhook' && (
            <Input
              label="Webhook URL"
              placeholder="https://api.example.com/reports"
              value={newChannel.config?.url || ''}
              onChange={(e) => updateConfig('url', e.target.value)}
            />
          )}

          <Button variant="outline" onClick={addChannel} icon={<Plus className="w-4 h-4" />} fullWidth>
            Add Channel
          </Button>
        </div>
      </Card>
    </div>
  )
}
