/**
 * DeliveryLog Component
 * Track report delivery status and history
 */

import { CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react'
import { Card } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Table } from './ui/Table'
import type { DeliveryLog as DeliveryLogType } from '../services/api'

interface DeliveryLogProps {
  logs: DeliveryLogType[]
  onResend: (deliveryId: string) => Promise<void>
}

export function DeliveryLog({ logs, onResend }: DeliveryLogProps) {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'sent':
        return <Badge variant="success" size="sm">Sent</Badge>
      case 'failed':
        return <Badge variant="danger" size="sm">Failed</Badge>
      case 'pending':
        return <Badge variant="warning" size="sm">Pending</Badge>
      default:
        return <Badge variant="secondary" size="sm">{status}</Badge>
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-400" />
      default:
        return null
    }
  }

  const columns = [
    { key: 'status', header: 'Status', width: '100px' },
    { key: 'report_name', header: 'Report' },
    { key: 'schedule_name', header: 'Schedule' },
    { key: 'channel', header: 'Channel' },
    { key: 'recipient', header: 'Recipient' },
    { key: 'sent_at', header: 'Sent At' },
    { key: 'actions', header: 'Actions', width: '120px' },
  ]

  const rows = logs.map((log) => ({
    status: (
      <div className="flex items-center gap-2">
        {getStatusIcon(log.status)}
        {getStatusBadge(log.status)}
      </div>
    ),
    report_name: log.report_name,
    schedule_name: log.schedule_name,
    channel: <Badge variant="info" size="sm">{log.channel}</Badge>,
    recipient: log.recipient,
    sent_at: new Date(log.sent_at).toLocaleString(),
    actions: log.status === 'failed' ? (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onResend(log.id)}
        icon={<RefreshCw className="w-4 h-4" />}
      >
        Resend
      </Button>
    ) : null,
  }))

  if (logs.length === 0) {
    return (
      <Card>
        <div className="p-12 text-center text-slate-500">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No delivery history yet</p>
          <p className="text-sm mt-1">Delivery logs will appear here</p>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Delivery History</h3>
        <div className="flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-400" />
            <span className="text-slate-400">
              {logs.filter((l) => l.status === 'sent').length} sent
            </span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="w-4 h-4 text-red-400" />
            <span className="text-slate-400">
              {logs.filter((l) => l.status === 'failed').length} failed
            </span>
          </div>
        </div>
      </div>

      <Card>
        <Table columns={columns} data={rows} striped />
      </Card>
    </div>
  )
}
