/**
 * Custom Hooks for Approval Workflow
 * Provides easy data fetching and mutation for approval requests
 */

import { useState, useCallback, useEffect } from 'react'
import {
  ApprovalRequest,
  ApprovalResponse,
  ApprovalFilter,
  ApprovalSort,
} from '../types/approval'

// Mock approval data for development
const mockApprovals: ApprovalRequest[] = [
  {
    id: 'APR-001',
    name: 'Q1 2026 Energy Report',
    type: 'report',
    submitter: 'John Smith',
    submitterId: 'user-001',
    submitterAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
    submittedDate: '2026-03-05',
    dueDate: '2026-03-15',
    status: 'under_review',
    priority: 'high',
    description: 'Quarterly energy consumption analysis for all facilities',
    assignees: ['manager@company.com'],
    comments: [
      {
        id: 'cmt-001',
        author: 'Sarah Johnson',
        authorId: 'user-002',
        text: 'Please update the renewable energy percentage calculations',
        timestamp: '2026-03-08T10:30:00Z',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
      },
    ],
    timeline: [
      {
        id: 'tl-001',
        action: 'Report submitted for review',
        actor: 'John Smith',
        timestamp: '2026-03-05T09:00:00Z',
        status: 'draft',
      },
      {
        id: 'tl-002',
        action: 'Moved to under review',
        actor: 'Sarah Johnson',
        timestamp: '2026-03-06T14:30:00Z',
        status: 'under_review',
      },
    ],
    approvalTrail: {
      maker: {
        name: 'John Smith',
        date: '2026-03-05',
        status: 'submitted',
      },
      checker: {
        name: 'Sarah Johnson',
        date: '2026-03-06',
        status: 'reviewing',
      },
    },
    slaDeadline: '2026-03-15',
    isEscalated: false,
    isOverdue: false,
  },
  {
    id: 'APR-002',
    name: 'Carbon Offset Calculation',
    type: 'calculation',
    submitter: 'Mike Chen',
    submitterId: 'user-003',
    submitterAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike',
    submittedDate: '2026-03-08',
    dueDate: '2026-03-12',
    status: 'draft',
    priority: 'medium',
    description: 'Carbon offset calculation for H1 2026',
    assignees: ['reviewer@company.com'],
    comments: [],
    timeline: [
      {
        id: 'tl-003',
        action: 'Calculation submitted',
        actor: 'Mike Chen',
        timestamp: '2026-03-08T11:00:00Z',
        status: 'draft',
      },
    ],
    approvalTrail: {
      maker: {
        name: 'Mike Chen',
        date: '2026-03-08',
        status: 'submitted',
      },
    },
    slaDeadline: '2026-03-12',
    isEscalated: false,
    isOverdue: false,
  },
  {
    id: 'APR-003',
    name: 'KPI Performance Metrics',
    type: 'metric',
    submitter: 'Emma Davis',
    submitterId: 'user-004',
    submitterAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma',
    submittedDate: '2026-02-28',
    dueDate: '2026-03-08',
    status: 'approved',
    priority: 'high',
    description: 'Monthly KPI metrics for performance dashboard',
    assignees: [],
    comments: [
      {
        id: 'cmt-002',
        author: 'Manager Admin',
        authorId: 'user-005',
        text: 'Approved. Great work on the PUE improvements!',
        timestamp: '2026-03-08T15:45:00Z',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Manager',
      },
    ],
    timeline: [
      {
        id: 'tl-004',
        action: 'Metrics submitted',
        actor: 'Emma Davis',
        timestamp: '2026-02-28T10:00:00Z',
        status: 'draft',
      },
      {
        id: 'tl-005',
        action: 'Under review',
        actor: 'Manager Admin',
        timestamp: '2026-03-01T09:30:00Z',
        status: 'under_review',
      },
      {
        id: 'tl-006',
        action: 'Approved',
        actor: 'Manager Admin',
        timestamp: '2026-03-08T15:45:00Z',
        status: 'approved',
      },
    ],
    approvalTrail: {
      maker: {
        name: 'Emma Davis',
        date: '2026-02-28',
        status: 'submitted',
      },
      reviewer: {
        name: 'Manager Admin',
        date: '2026-03-08',
        status: 'approved',
      },
    },
    slaDeadline: '2026-03-08',
    isEscalated: false,
    isOverdue: false,
  },
  {
    id: 'APR-004',
    name: 'Water Usage Report',
    type: 'report',
    submitter: 'Lisa Wong',
    submitterId: 'user-006',
    submitterAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa',
    submittedDate: '2026-02-25',
    dueDate: '2026-03-05',
    status: 'rejected',
    priority: 'medium',
    description: 'Monthly water consumption analysis',
    assignees: [],
    comments: [
      {
        id: 'cmt-003',
        author: 'Reviewer',
        authorId: 'user-007',
        text: 'Data inconsistencies found. Please revise and resubmit.',
        timestamp: '2026-03-03T11:20:00Z',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Reviewer',
      },
    ],
    timeline: [
      {
        id: 'tl-007',
        action: 'Report submitted',
        actor: 'Lisa Wong',
        timestamp: '2026-02-25T14:00:00Z',
        status: 'draft',
      },
      {
        id: 'tl-008',
        action: 'Rejected',
        actor: 'Reviewer',
        timestamp: '2026-03-03T11:20:00Z',
        status: 'rejected',
      },
    ],
    approvalTrail: {
      maker: {
        name: 'Lisa Wong',
        date: '2026-02-25',
        status: 'submitted',
      },
      reviewer: {
        name: 'Reviewer',
        date: '2026-03-03',
        status: 'rejected',
      },
    },
    slaDeadline: '2026-03-05',
    isEscalated: false,
    isOverdue: true,
  },
]

/**
 * Hook for fetching approvals list with filtering and pagination
 */
export function useApprovals(
  filter?: ApprovalFilter,
  sort?: ApprovalSort,
  page?: number,
  pageSize?: number
) {
  const [filteredApprovals, setFilteredApprovals] = useState<ApprovalRequest[]>(
    mockApprovals
  )

  // Filter and sort logic
  useEffect(() => {
    let result = [...mockApprovals]

    // Apply filters
    if (filter?.status && filter.status.length > 0) {
      result = result.filter((a) => filter.status!.includes(a.status))
    }

    if (filter?.type && filter.type.length > 0) {
      result = result.filter((a) => filter.type!.includes(a.type))
    }

    if (filter?.search) {
      const searchLower = filter.search.toLowerCase()
      result = result.filter(
        (a) =>
          a.name.toLowerCase().includes(searchLower) ||
          a.submitter.toLowerCase().includes(searchLower) ||
          a.id.toLowerCase().includes(searchLower)
      )
    }

    // Apply sorting
    if (sort) {
      result.sort((a, b) => {
        let aVal: any, bVal: any

        switch (sort.field) {
          case 'due_date':
            aVal = new Date(a.dueDate).getTime()
            bVal = new Date(b.dueDate).getTime()
            break
          case 'submitted_date':
            aVal = new Date(a.submittedDate).getTime()
            bVal = new Date(b.submittedDate).getTime()
            break
          case 'priority':
            const priorityMap = { high: 3, medium: 2, low: 1 }
            aVal = priorityMap[a.priority]
            bVal = priorityMap[b.priority]
            break
          case 'status':
            aVal = a.status
            bVal = b.status
            break
          default:
            return 0
        }

        return sort.direction === 'asc' ? aVal - bVal : bVal - aVal
      })
    }

    setFilteredApprovals(result)
  }, [filter, sort])

  const totalPages = Math.ceil(filteredApprovals.length / (pageSize || 10))
  const startIdx = ((page || 1) - 1) * (pageSize || 10)
  const paginatedApprovals = filteredApprovals.slice(
    startIdx,
    startIdx + (pageSize || 10)
  )

  return {
    data: {
      approvals: paginatedApprovals,
      total: filteredApprovals.length,
      pages: totalPages,
      pendingCount: mockApprovals.filter(
        (a) => a.status === 'draft' || a.status === 'under_review'
      ).length,
    } as ApprovalResponse,
    loading: false,
    error: null,
  }
}

/**
 * Hook for fetching single approval detail
 */
export function useApprovalDetail(approvalId: string) {
  const approval = mockApprovals.find((a) => a.id === approvalId)

  return {
    data: approval || null,
    loading: false,
    error: approval ? null : { status: 404, message: 'Approval not found' },
  }
}

/**
 * Hook for pending approvals count
 */
export function usePendingApprovalsCount() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const updateCount = () => {
      const pendingCount = mockApprovals.filter(
        (a) => a.status === 'draft' || a.status === 'under_review'
      ).length
      setCount(pendingCount)
    }

    updateCount()

    // Refresh every 30 seconds
    const interval = setInterval(updateCount, 30000)

    return () => clearInterval(interval)
  }, [])

  return count
}

/**
 * Hook for approval actions (approve, reject, comment)
 */
export function useApprovalAction(approvalId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const approve = useCallback(
    async (reason?: string) => {
      setLoading(true)
      setError(null)
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        const approval = mockApprovals.find((a) => a.id === approvalId)
        if (approval) {
          approval.status = 'approved'
          approval.timeline.push({
            id: `tl-${Date.now()}`,
            action: 'Approved',
            actor: 'Current User',
            timestamp: new Date().toISOString(),
            status: 'approved',
            comment: reason,
          })
        }

        return true
      } catch (err) {
        setError('Failed to approve')
        return false
      } finally {
        setLoading(false)
      }
    },
    [approvalId]
  )

  const reject = useCallback(
    async (reason: string) => {
      setLoading(true)
      setError(null)
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1000))

        const approval = mockApprovals.find((a) => a.id === approvalId)
        if (approval) {
          approval.status = 'rejected'
          approval.timeline.push({
            id: `tl-${Date.now()}`,
            action: 'Rejected',
            actor: 'Current User',
            timestamp: new Date().toISOString(),
            status: 'rejected',
            comment: reason,
          })
        }

        return true
      } catch (err) {
        setError('Failed to reject')
        return false
      } finally {
        setLoading(false)
      }
    },
    [approvalId]
  )

  const addComment = useCallback(
    async (text: string) => {
      setLoading(true)
      setError(null)
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 500))

        const approval = mockApprovals.find((a) => a.id === approvalId)
        if (approval) {
          approval.comments.push({
            id: `cmt-${Date.now()}`,
            author: 'Current User',
            authorId: 'current-user',
            text,
            timestamp: new Date().toISOString(),
          })
        }

        return true
      } catch (err) {
        setError('Failed to add comment')
        return false
      } finally {
        setLoading(false)
      }
    },
    [approvalId]
  )

  return { approve, reject, addComment, loading, error }
}
