/**
 * Approvals Workflow Dashboard
 * Main page for managing approval requests
 */

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  Pagination,
  Spinner,
  EmptyState,
} from '../components/ui'
import { ApprovalCard } from '../components/ApprovalCard'
import { ApprovalDetail } from '../components/ApprovalDetail'
import { ApprovalFilters } from '../components/ApprovalFilters'
import { useApprovals, useApprovalDetail, useApprovalAction } from '../hooks/useApprovals'
import { ApprovalFilter, ApprovalSort } from '../types/approval'
import { CheckCircle, AlertCircle, Clock } from 'lucide-react'

export function Approvals() {
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState<ApprovalFilter>({})
  const [sort, setSort] = useState<ApprovalSort>({
    field: 'due_date',
    direction: 'asc',
  })
  const [selectedApprovalId, setSelectedApprovalId] = useState<string | null>(null)

  // Fetch approvals data
  const approvalsData = useApprovals(filters, sort, currentPage, 10)

  // Fetch selected approval detail
  const selectedApprovalDetail = useApprovalDetail(selectedApprovalId || '')
  const selectedApproval =
    selectedApprovalId && selectedApprovalDetail.data
      ? selectedApprovalDetail.data
      : null

  // Approval actions
  const approvalActions = useApprovalAction(selectedApprovalId || '')

  // Statistics
  const stats = [
    {
      label: 'Pending',
      value: approvalsData.data?.pendingCount || 0,
      icon: <Clock className="w-6 h-6 text-blue-400" />,
      color: 'from-blue-600/20 to-blue-900/20',
    },
    {
      label: 'Approved',
      value: approvalsData.data?.approvals.filter((a) => a.status === 'approved')
        .length || 0,
      icon: <CheckCircle className="w-6 h-6 text-green-400" />,
      color: 'from-green-600/20 to-green-900/20',
    },
    {
      label: 'Rejected',
      value: approvalsData.data?.approvals.filter((a) => a.status === 'rejected')
        .length || 0,
      icon: <AlertCircle className="w-6 h-6 text-red-400" />,
      color: 'from-red-600/20 to-red-900/20',
    },
  ]

  const handleFilterChange = (newFilters: ApprovalFilter) => {
    setFilters(newFilters)
    setCurrentPage(1)
  }

  const handleSortChange = (field: string, direction: string) => {
    setSort({
      field: field as ApprovalSort['field'],
      direction: direction as 'asc' | 'desc',
    })
    setCurrentPage(1)
  }

  const handleApprove = async (reason?: string) => {
    const success = await approvalActions.approve(reason)
    if (success) {
      setSelectedApprovalId(null)
      // Refetch approvals
    }
  }

  const handleReject = async (reason: string) => {
    const success = await approvalActions.reject(reason)
    if (success) {
      setSelectedApprovalId(null)
      // Refetch approvals
    }
  }

  const handleAddComment = async (text: string) => {
    const success = await approvalActions.addComment(text)
    if (success) {
      // Comment added successfully
    }
  }

  // Show detail view if an approval is selected
  if (selectedApproval) {
    return (
      <div className="space-y-6">
        <ApprovalDetail
          approval={selectedApproval}
          isLoading={approvalActions.loading}
          onApprove={handleApprove}
          onReject={handleReject}
          onAddComment={handleAddComment}
          onBack={() => setSelectedApprovalId(null)}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl md:text-4xl font-bold text-white">
          Approval Workflow
        </h1>
        <p className="text-slate-400 mt-2">
          Manage and track approval requests for reports, calculations, and metrics
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat) => (
          <Card key={stat.label} className="relative overflow-hidden">
            <div
              className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-30`}
            />
            <CardContent className="p-6 relative z-10">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">{stat.label}</p>
                  <p className="text-3xl font-bold text-white mt-2">
                    {stat.value}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-slate-800/50">
                  {stat.icon}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filters & Search</CardTitle>
          <CardDescription>
            Find approvals by status, type, assignee, or search term
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ApprovalFilters
            onFilterChange={handleFilterChange}
            onSortChange={handleSortChange}
          />
        </CardContent>
      </Card>

      {/* Approvals List */}
      <div>
        <div className="mb-4">
          <h2 className="text-xl font-bold text-white">
            Approvals
            {approvalsData.data?.total ? (
              <span className="text-slate-400 font-normal">
                {' '}
                ({approvalsData.data.total})
              </span>
            ) : null}
          </h2>
        </div>

        {approvalsData.loading ? (
          <div className="flex items-center justify-center py-12">
            <Spinner />
          </div>
        ) : !approvalsData.data?.approvals || approvalsData.data.approvals.length === 0 ? (
          <EmptyState
            title="No Approvals Found"
            description="There are no approval requests matching your filters. Create a new request or adjust your search criteria."
            icon={CheckCircle}
          />
        ) : (
          <div className="space-y-4">
            {approvalsData.data.approvals.map((approval) => (
              <ApprovalCard
                key={approval.id}
                approval={approval}
                onApprove={(id) => setSelectedApprovalId(id)}
                onReject={(id) => setSelectedApprovalId(id)}
                onComment={(id) => setSelectedApprovalId(id)}
                onClick={setSelectedApprovalId}
                isLoading={approvalActions.loading}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {approvalsData.data?.pages && approvalsData.data.pages > 1 && (
          <div className="mt-6 flex justify-center">
            <Pagination
              currentPage={currentPage}
              totalPages={approvalsData.data.pages}
              onPageChange={setCurrentPage}
            />
          </div>
        )}
      </div>

      {/* SLA and Escalation Info */}
      {approvalsData.data?.approvals && approvalsData.data.approvals.some(
        (a) => a.isOverdue || a.isEscalated
      ) && (
        <Card className="border-orange-600/30 bg-orange-600/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-orange-400" />
              Attention Needed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-orange-300">
              {approvalsData.data.approvals
                .filter((a) => a.isOverdue)
                .map((a) => (
                  <li key={a.id}>
                    • <strong>{a.name}</strong> is overdue
                  </li>
                ))}
              {approvalsData.data.approvals
                .filter((a) => a.isEscalated)
                .map((a) => (
                  <li key={a.id}>
                    • <strong>{a.name}</strong> has been escalated
                  </li>
                ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
