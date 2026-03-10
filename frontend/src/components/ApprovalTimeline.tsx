/**
 * Approval Timeline Component
 * Visual timeline of approval progression
 */

import { TimelineEntry, ApprovalStatus } from '../types/approval'
import {
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  FileCheck,
} from 'lucide-react'

interface ApprovalTimelineProps {
  timeline: TimelineEntry[]
  currentStatus: ApprovalStatus
}

const statusIcons: Record<ApprovalStatus, React.ReactNode> = {
  draft: <FileCheck className="w-5 h-5" />,
  under_review: <Eye className="w-5 h-5" />,
  approved: <CheckCircle className="w-5 h-5" />,
  rejected: <XCircle className="w-5 h-5" />,
}

const statusColors: Record<ApprovalStatus, string> = {
  draft: 'bg-slate-600',
  under_review: 'bg-blue-600',
  approved: 'bg-green-600',
  rejected: 'bg-red-600',
}

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function ApprovalTimeline({
  timeline,
  currentStatus,
}: ApprovalTimelineProps) {
  if (timeline.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400">
        <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No timeline entries yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {/* Title */}
      <h3 className="font-semibold text-white mb-6 flex items-center gap-2">
        <Clock className="w-5 h-5 text-slate-400" />
        Approval Timeline
      </h3>

      {/* Timeline */}
      <div className="relative space-y-4">
        {timeline.map((entry, index) => {
          const isActive = entry.status === currentStatus
          const isCompleted = index < timeline.length - 1 || isActive

          return (
            <div key={entry.id} className="flex gap-4">
              {/* Timeline Line and Node */}
              <div className="flex flex-col items-center">
                {/* Connector Line - Top */}
                {index > 0 && (
                  <div
                    className={`w-0.5 h-3 ${
                      isCompleted ? 'bg-green-600/50' : 'bg-slate-600/30'
                    }`}
                  />
                )}

                {/* Status Node */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isActive
                      ? statusColors[entry.status]
                      : isCompleted
                        ? 'bg-green-600/30'
                        : 'bg-slate-700'
                  } text-white flex-shrink-0 border-2 ${
                    isActive
                      ? 'border-white'
                      : isCompleted
                        ? 'border-green-600/50'
                        : 'border-slate-600'
                  }`}
                >
                  {isCompleted && !isActive ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    statusIcons[entry.status]
                  )}
                </div>

                {/* Connector Line - Bottom */}
                {index < timeline.length - 1 && (
                  <div
                    className={`w-0.5 h-12 ${
                      isCompleted ? 'bg-green-600/50' : 'bg-slate-600/30'
                    }`}
                  />
                )}
              </div>

              {/* Timeline Entry Content */}
              <div className="pb-4 flex-1 pt-1">
                <div className="flex items-baseline gap-2 flex-wrap">
                  <h4 className="font-semibold text-white text-sm md:text-base">
                    {entry.action}
                  </h4>
                  <span className="text-xs text-slate-500 whitespace-nowrap">
                    {formatTime(entry.timestamp)}
                  </span>
                </div>

                <p className="text-sm text-slate-400 mt-1">
                  by <span className="text-slate-300 font-medium">{entry.actor}</span>
                </p>

                {entry.comment && (
                  <div className="mt-2 p-3 rounded-lg bg-slate-800/40 border border-slate-700/20">
                    <p className="text-sm text-slate-300">{entry.comment}</p>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Status Badge */}
      <div className="mt-6 pt-4 border-t border-slate-700/30">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">Current Status:</span>
          <div
            className={`flex items-center gap-1 px-3 py-1 rounded text-sm font-medium text-white ${
              statusColors[currentStatus]
            }`}
          >
            {statusIcons[currentStatus]}
            <span className="capitalize">{currentStatus.replace('_', ' ')}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
