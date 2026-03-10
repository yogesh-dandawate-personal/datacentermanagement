/**
 * Approval Detail Component
 * Full detail view for a single approval request
 */

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  Badge,
  Button,
  Alert,
  Dialog,
  Textarea,
} from './ui'
import { ApprovalRequest } from '../types/approval'
import { ApprovalTimeline } from './ApprovalTimeline'
import { CommentThread } from './CommentThread'
import {
  ArrowLeft,
  CheckCircle,
  XCircle,
  FileText,
  Calculator,
  TrendingUp,
} from 'lucide-react'

interface ApprovalDetailProps {
  approval: ApprovalRequest
  isLoading?: boolean
  onApprove: (reason?: string) => void
  onReject: (reason: string) => void
  onAddComment: (text: string) => void
  onBack: () => void
}

const statusBadgeColors: Record<string, string> = {
  draft: 'bg-slate-600',
  under_review: 'bg-blue-600',
  approved: 'bg-green-600',
  rejected: 'bg-red-600',
}

const typeIcons: Record<string, React.ReactNode> = {
  report: <FileText className="w-5 h-5" />,
  calculation: <Calculator className="w-5 h-5" />,
  metric: <TrendingUp className="w-5 h-5" />,
}

const typeLabels: Record<string, string> = {
  report: 'Report',
  calculation: 'Calculation',
  metric: 'Metric',
}

export function ApprovalDetail({
  approval,
  isLoading = false,
  onApprove,
  onReject,
  onAddComment,
  onBack,
}: ApprovalDetailProps) {
  const [showApproveDialog, setShowApproveDialog] = useState(false)
  const [showRejectDialog, setShowRejectDialog] = useState(false)
  const [approvalReason, setApprovalReason] = useState('')
  const [rejectionReason, setRejectionReason] = useState('')

  const daysUntilDue = Math.ceil(
    (new Date(approval.dueDate).getTime() - new Date().getTime()) /
      (1000 * 60 * 60 * 24)
  )
  const isApproachingDeadline = daysUntilDue <= 3 && daysUntilDue > 0

  const canApprove =
    approval.status === 'draft' || approval.status === 'under_review'
  const canReject =
    approval.status === 'draft' || approval.status === 'under_review'

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Approvals
      </button>

      {/* Main Card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {typeIcons[approval.type]}
                <CardTitle>{approval.name}</CardTitle>
              </div>
              <CardDescription className="text-base">
                {approval.id}
              </CardDescription>
            </div>
            <Badge className={`${statusBadgeColors[approval.status]} text-white`}>
              {approval.status.replace('_', ' ')}
            </Badge>
          </div>

          {approval.description && (
            <p className="text-slate-300 mt-4">{approval.description}</p>
          )}
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Alert for Overdue/Approaching Deadline */}
          {approval.isOverdue && (
            <Alert
              variant="error"
              title="Overdue"
              message="This approval request is past its due date."
            />
          )}

          {isApproachingDeadline && !approval.isOverdue && (
            <Alert
              variant="warning"
              title="Approaching Deadline"
              message={`${daysUntilDue} days remaining to complete approval.`}
            />
          )}

          {approval.isEscalated && (
            <Alert
              variant="info"
              title="Escalated"
              message={`This approval has been escalated to ${approval.escalatedTo}.`}
            />
          )}

          {/* Key Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-500 mb-1">Type</p>
              <p className="text-white font-medium">
                {typeLabels[approval.type]}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-500 mb-1">Priority</p>
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
            <div>
              <p className="text-sm text-slate-500 mb-1">Submitter</p>
              <p className="text-white">{approval.submitter}</p>
            </div>
            <div>
              <p className="text-sm text-slate-500 mb-1">Submitted Date</p>
              <p className="text-white">
                {new Date(approval.submittedDate).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-500 mb-1">Due Date</p>
              <p className="text-white">
                {new Date(approval.dueDate).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-500 mb-1">SLA Deadline</p>
              <p className="text-white">
                {new Date(approval.slaDeadline).toLocaleDateString()}
              </p>
            </div>
          </div>

          {/* Assignees */}
          {approval.assignees.length > 0 && (
            <div>
              <p className="text-sm text-slate-500 mb-2">Assigned To</p>
              <div className="flex flex-wrap gap-2">
                {approval.assignees.map((assignee) => (
                  <span
                    key={assignee}
                    className="px-3 py-1 rounded-full bg-slate-800 text-slate-300 text-sm"
                  >
                    {assignee}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Data Section */}
          {approval.data && (
            <div className="border-t border-slate-700/30 pt-6">
              <h4 className="font-semibold text-white mb-4">Data Being Reviewed</h4>
              <div className="space-y-3">
                {approval.data.metrics && (
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Metrics:</p>
                    <pre className="bg-slate-800/50 p-3 rounded text-xs text-slate-300 overflow-auto">
                      {JSON.stringify(approval.data.metrics, null, 2)}
                    </pre>
                  </div>
                )}
                {approval.data.calculations && (
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Calculations:</p>
                    <pre className="bg-slate-800/50 p-3 rounded text-xs text-slate-300 overflow-auto">
                      {JSON.stringify(approval.data.calculations, null, 2)}
                    </pre>
                  </div>
                )}
                {approval.data.evidence && (
                  <div>
                    <p className="text-sm text-slate-400 mb-2">Evidence Files:</p>
                    <ul className="space-y-1">
                      {approval.data.evidence.map((file, idx) => (
                        <li key={idx} className="text-sm text-slate-300">
                          • {file}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card>
        <CardContent className="p-6">
          <ApprovalTimeline timeline={approval.timeline} currentStatus={approval.status} />
        </CardContent>
      </Card>

      {/* Comments */}
      <Card>
        <CardContent className="p-6">
          <CommentThread
            comments={approval.comments}
            onAddComment={onAddComment}
            isLoading={isLoading}
            isReadOnly={approval.status === 'approved' || approval.status === 'rejected'}
          />
        </CardContent>
      </Card>

      {/* Action Buttons */}
      {canApprove || canReject ? (
        <div className="flex gap-3 flex-wrap">
          {canApprove && (
            <Button
              onClick={() => setShowApproveDialog(true)}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Approve
            </Button>
          )}
          {canReject && (
            <Button
              onClick={() => setShowRejectDialog(true)}
              variant="danger"
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              <XCircle className="w-4 h-4" />
              Reject
            </Button>
          )}
        </div>
      ) : (
        <Alert
          variant="info"
          message={`This approval request cannot be modified as it has already been ${
            approval.status === 'approved' ? 'approved' : 'rejected'
          }.`}
        />
      )}

      {/* Approve Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <div className="space-y-4 p-6">
          <h2 className="text-xl font-semibold text-white">Approve Request</h2>
          <p className="text-slate-300">
            Are you sure you want to approve this request? You can add an optional
            reason below.
          </p>
          <Textarea
            value={approvalReason}
            onChange={(e) => setApprovalReason(e.target.value)}
            placeholder="Reason for approval (optional)..."
            className="min-h-20"
          />
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowApproveDialog(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                onApprove(approvalReason || undefined)
                setShowApproveDialog(false)
                setApprovalReason('')
              }}
              loading={isLoading}
            >
              Confirm Approval
            </Button>
          </div>
        </div>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <div className="space-y-4 p-6">
          <h2 className="text-xl font-semibold text-white">Reject Request</h2>
          <p className="text-slate-300">
            Please provide a reason for rejection. This will be shared with the
            submitter.
          </p>
          <Textarea
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="Reason for rejection..."
            className="min-h-20"
            required
          />
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowRejectDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                if (rejectionReason.trim()) {
                  onReject(rejectionReason)
                  setShowRejectDialog(false)
                  setRejectionReason('')
                }
              }}
              loading={isLoading}
              disabled={!rejectionReason.trim()}
            >
              Confirm Rejection
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}
