/**
 * Approval Card Component
 * Displays a single approval request in card format
 */

import { useState } from 'react'
import { Card, CardContent, Badge, Button } from './ui'
import { ApprovalRequest, ApprovalStatus } from '../types/approval'
import {
  Clock,
  FileText,
  Calculator,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle,
  MessageSquare,
} from 'lucide-react'

interface ApprovalCardProps {
  approval: ApprovalRequest
  onApprove: (id: string) => void
  onReject: (id: string) => void
  onComment: (id: string) => void
  onClick: (id: string) => void
  isLoading?: boolean
}

const statusColors: Record<ApprovalStatus, string> = {
  draft: 'bg-slate-600 text-white',
  under_review: 'bg-blue-600 text-white',
  approved: 'bg-green-600 text-white',
  rejected: 'bg-red-600 text-white',
}

const statusLabels: Record<ApprovalStatus, string> = {
  draft: 'Draft',
  under_review: 'Under Review',
  approved: 'Approved',
  rejected: 'Rejected',
}

const typeIcons: Record<string, React.ReactNode> = {
  report: <FileText className="w-4 h-4" />,
  calculation: <Calculator className="w-4 h-4" />,
  metric: <TrendingUp className="w-4 h-4" />,
}

const typeLabels: Record<string, string> = {
  report: 'Report',
  calculation: 'Calculation',
  metric: 'Metric',
}

export function ApprovalCard({
  approval,
  onApprove,
  onReject,
  onComment,
  onClick,
  isLoading = false,
}: ApprovalCardProps) {
  const [showQuickActions, setShowQuickActions] = useState(false)
  const isOverdue = approval.isOverdue
  const daysUntilDue = Math.ceil(
    (new Date(approval.dueDate).getTime() - new Date().getTime()) /
      (1000 * 60 * 60 * 24)
  )
  const isApproachingDeadline = daysUntilDue <= 3 && daysUntilDue > 0

  return (
    <Card
      className="hover:border-slate-600/50 transition-all cursor-pointer"
      onMouseEnter={() => setShowQuickActions(true)}
      onMouseLeave={() => setShowQuickActions(false)}
    >
      <CardContent className="p-4 md:p-6">
        {/* Header Section */}
        <div
          className="mb-4 cursor-pointer"
          onClick={() => onClick(approval.id)}
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                {typeIcons[approval.type]}
                <h3 className="text-white font-semibold text-sm md:text-base">
                  {approval.name}
                </h3>
              </div>
              <p className="text-slate-400 text-xs md:text-sm">
                {approval.id}
              </p>
            </div>
            <Badge className={`${statusColors[approval.status]} text-xs`}>
              {statusLabels[approval.status]}
            </Badge>
          </div>
        </div>

        {/* Approval Trail */}
        <div className="mb-4 text-xs md:text-sm text-slate-300 bg-slate-800/30 rounded-lg p-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            {approval.approvalTrail.maker && (
              <div>
                <p className="text-slate-500 text-xs">Maker</p>
                <p className="font-medium">{approval.approvalTrail.maker.name}</p>
                <p className="text-slate-400 text-xs">
                  {approval.approvalTrail.maker.date}
                </p>
              </div>
            )}
            {approval.approvalTrail.checker && (
              <div>
                <p className="text-slate-500 text-xs">Checker</p>
                <p className="font-medium">{approval.approvalTrail.checker.name}</p>
                <p className="text-slate-400 text-xs">
                  {approval.approvalTrail.checker.date}
                </p>
              </div>
            )}
            {approval.approvalTrail.reviewer && (
              <div>
                <p className="text-slate-500 text-xs">Reviewer</p>
                <p className="font-medium">
                  {approval.approvalTrail.reviewer.name}
                </p>
                <p className="text-slate-400 text-xs">
                  {approval.approvalTrail.reviewer.date}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="mb-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs md:text-sm">
          <div>
            <p className="text-slate-500 mb-1">Submitter</p>
            <p className="text-slate-200">{approval.submitter}</p>
          </div>
          <div>
            <p className="text-slate-500 mb-1">Submitted</p>
            <p className="text-slate-200">
              {new Date(approval.submittedDate).toLocaleDateString()}
            </p>
          </div>
          <div>
            <p className="text-slate-500 mb-1">Type</p>
            <p className="text-slate-200">{typeLabels[approval.type]}</p>
          </div>
          <div>
            <p className="text-slate-500 mb-1">Priority</p>
            <p
              className={`font-medium capitalize ${
                approval.priority === 'high'
                  ? 'text-red-400'
                  : approval.priority === 'medium'
                    ? 'text-yellow-400'
                    : 'text-green-400'
              }`}
            >
              {approval.priority}
            </p>
          </div>
        </div>

        {/* Due Date and SLA */}
        <div className="mb-4 flex flex-col md:flex-row md:items-center gap-3">
          <div className="flex items-center gap-2 text-xs md:text-sm">
            <Clock className="w-4 h-4 text-slate-400" />
            <span className="text-slate-300">
              Due: {new Date(approval.dueDate).toLocaleDateString()}
            </span>
            {isOverdue && (
              <span className="flex items-center gap-1 px-2 py-1 rounded bg-red-600/20 text-red-400">
                <AlertCircle className="w-3 h-3" />
                Overdue
              </span>
            )}
            {isApproachingDeadline && !isOverdue && (
              <span className="flex items-center gap-1 px-2 py-1 rounded bg-yellow-600/20 text-yellow-400">
                <AlertCircle className="w-3 h-3" />
                {daysUntilDue} days left
              </span>
            )}
          </div>
          {approval.isEscalated && (
            <span className="px-2 py-1 rounded text-xs bg-orange-600/20 text-orange-400">
              Escalated to {approval.escalatedTo}
            </span>
          )}
        </div>

        {/* Comments Count */}
        <div className="mb-4 flex items-center gap-2 text-slate-400 text-xs md:text-sm">
          <MessageSquare className="w-4 h-4" />
          <span>{approval.comments.length} comments</span>
        </div>

        {/* Action Buttons */}
        <div
          className={`flex gap-2 flex-wrap transition-all ${
            showQuickActions ? 'opacity-100 visible' : 'opacity-0 md:opacity-100'
          }`}
        >
          {approval.status === 'draft' || approval.status === 'under_review' ? (
            <>
              <Button
                size="sm"
                variant="primary"
                onClick={() => onApprove(approval.id)}
                disabled={isLoading}
                className="text-xs"
              >
                <CheckCircle className="w-3 h-3 mr-1" />
                Approve
              </Button>
              <Button
                size="sm"
                variant="danger"
                onClick={() => onReject(approval.id)}
                disabled={isLoading}
                className="text-xs"
              >
                <XCircle className="w-3 h-3 mr-1" />
                Reject
              </Button>
            </>
          ) : null}
          <Button
            size="sm"
            variant="outline"
            onClick={() => onComment(approval.id)}
            disabled={isLoading}
            className="text-xs"
          >
            <MessageSquare className="w-3 h-3 mr-1" />
            Comment
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onClick(approval.id)}
            className="ml-auto text-xs"
          >
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
