/**
 * Approval Workflow Types
 * Defines data structures for approval request handling
 */

export type ApprovalStatus = 'draft' | 'under_review' | 'approved' | 'rejected'
export type ApprovalType = 'report' | 'calculation' | 'metric'
export type ApprovalAction = 'approve' | 'request_changes' | 'comment'

export interface TimelineEntry {
  id: string
  action: string
  actor: string
  timestamp: string
  comment?: string
  status: ApprovalStatus
  avatar?: string
}

export interface ApprovalComment {
  id: string
  author: string
  authorId: string
  text: string
  timestamp: string
  avatar?: string
  edited?: boolean
  editedAt?: string
}

export interface ApprovalRequest {
  id: string
  name: string
  type: ApprovalType
  submitter: string
  submitterId: string
  submitterAvatar?: string
  submittedDate: string
  dueDate: string
  status: ApprovalStatus
  priority: 'low' | 'medium' | 'high'
  description?: string
  assignees: string[]
  comments: ApprovalComment[]
  timeline: TimelineEntry[]
  approvalTrail: {
    maker?: {
      name: string
      date: string
      status: string
    }
    checker?: {
      name: string
      date: string
      status: string
    }
    reviewer?: {
      name: string
      date: string
      status: string
    }
  }
  data?: {
    metrics?: Record<string, any>
    calculations?: Record<string, any>
    evidence?: string[]
  }
  slaDeadline: string
  isEscalated: boolean
  escalatedTo?: string
  isOverdue: boolean
  previousVersions?: ApprovalVersion[]
}

export interface ApprovalVersion {
  id: string
  version: number
  createdAt: string
  createdBy: string
  changes: string[]
}

export interface ApprovalFilter {
  status?: ApprovalStatus[]
  type?: ApprovalType[]
  assignee?: 'me' | 'my_team' | 'all'
  search?: string
}

export interface ApprovalSort {
  field: 'due_date' | 'submitted_date' | 'priority' | 'status'
  direction: 'asc' | 'desc'
}

export interface ApprovalResponse {
  approvals: ApprovalRequest[]
  total: number
  pages: number
  pendingCount: number
}

export interface ApprovalDetailResponse {
  approval: ApprovalRequest
}
