/**
 * Remediation Tasks Component
 * Displays and manages tasks required to close compliance gaps
 */

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Button, SkeletonTable, Checkbox } from './ui'
import { ChevronDown, User, Calendar, Zap, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import { RemediationTask, TaskStatus, TaskPriority } from '../types/compliance'

interface RemediationTasksProps {
  tasks: RemediationTask[] | null
  loading: boolean
}

interface ExpandedTasks {
  [key: string]: boolean
}

type TaskStatusFilter = 'All' | 'Assigned' | 'In Progress' | 'Completed'
type TaskPriorityFilter = 'All' | 'P0' | 'P1' | 'P2' | 'P3'

export function RemediationTasks({ tasks, loading }: RemediationTasksProps) {
  const [expandedTasks, setExpandedTasks] = useState<ExpandedTasks>({})
  const [statusFilter, setStatusFilter] = useState<TaskStatusFilter>('All')
  const [priorityFilter, setPriorityFilter] = useState<TaskPriorityFilter>('All')
  const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set())

  const toggleTask = (id: string) => {
    setExpandedTasks((prev) => ({
      ...prev,
      [id]: !prev[id],
    }))
  }

  const toggleTaskComplete = (id: string) => {
    setCompletedTasks((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Remediation Tasks</CardTitle>
          <CardDescription>Tasks required to close compliance gaps</CardDescription>
        </CardHeader>
        <CardContent>
          <SkeletonTable rows={5} cols={4} />
        </CardContent>
      </Card>
    )
  }

  if (!tasks || tasks.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Remediation Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-slate-400">No remediation tasks assigned</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Filter tasks
  const filteredTasks = tasks.filter((t) => {
    const statusMatch = statusFilter === 'All' || t.status === statusFilter
    const priorityMatch = priorityFilter === 'All' || t.priority === priorityFilter
    return statusMatch && priorityMatch
  })

  // Get task status icon
  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case 'Completed':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'In Progress':
        return <Clock className="w-5 h-5 text-blue-400" />
      case 'Assigned':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />
    }
  }

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-500/10 border-green-500/20'
      case 'In Progress':
        return 'bg-blue-500/10 border-blue-500/20'
      case 'Assigned':
        return 'bg-yellow-500/10 border-yellow-500/20'
    }
  }

  const getStatusBadgeVariant = (status: TaskStatus) => {
    switch (status) {
      case 'Completed':
        return 'success' as const
      case 'In Progress':
        return 'info' as const
      case 'Assigned':
        return 'warning' as const
    }
  }

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'P0':
        return 'bg-red-500/20 text-red-300'
      case 'P1':
        return 'bg-orange-500/20 text-orange-300'
      case 'P2':
        return 'bg-yellow-500/20 text-yellow-300'
      case 'P3':
        return 'bg-blue-500/20 text-blue-300'
    }
  }

  // Calculate task counts
  const assignedCount = tasks.filter((t) => t.status === 'Assigned').length
  const inProgressCount = tasks.filter((t) => t.status === 'In Progress').length
  const completedCount = tasks.filter((t) => t.status === 'Completed').length

  // Calculate overdue tasks
  const today = new Date()
  const overdueCount = tasks.filter((t) => t.status !== 'Completed' && new Date(t.dueDate) < today).length

  // Calculate days until deadline
  const daysUntilDeadline = (dueDate: string): number => {
    const deadline = new Date(dueDate)
    const diffTime = deadline.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  }

  const getDeadlineStatus = (dueDate: string) => {
    const days = daysUntilDeadline(dueDate)
    if (days < 0) return { text: 'Overdue', color: 'text-red-500', bgColor: 'bg-red-500/10' }
    if (days < 7) return { text: `${days} days left`, color: 'text-red-400', bgColor: 'bg-red-500/10' }
    if (days < 30) return { text: `${days} days left`, color: 'text-yellow-400', bgColor: 'bg-yellow-500/10' }
    return { text: `${days} days left`, color: 'text-green-400', bgColor: 'bg-green-500/10' }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Remediation Tasks</CardTitle>
            <CardDescription>Tasks required to close compliance gaps</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{tasks.length}</div>
            <p className="text-xs text-slate-400">Total Tasks</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Status Summary */}
        <div className="grid grid-cols-4 gap-3">
          <Card variant="default" className="bg-yellow-500/10 border-yellow-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-yellow-400 font-medium mb-1">ASSIGNED</p>
                <p className="text-2xl font-bold text-yellow-400">{assignedCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-blue-500/10 border-blue-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-blue-400 font-medium mb-1">IN PROGRESS</p>
                <p className="text-2xl font-bold text-blue-400">{inProgressCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-green-500/10 border-green-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-green-400 font-medium mb-1">COMPLETED</p>
                <p className="text-2xl font-bold text-green-400">{completedCount}</p>
              </div>
            </CardContent>
          </Card>

          <Card variant="default" className="bg-red-500/10 border-red-500/20">
            <CardContent className="pt-4">
              <div className="text-center">
                <p className="text-xs text-red-400 font-medium mb-1">OVERDUE</p>
                <p className="text-2xl font-bold text-red-400">{overdueCount}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <div className="space-y-3">
          <div className="flex gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 self-center">Status:</span>
            {(['All', 'Assigned', 'In Progress', 'Completed'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-blue-500/30 border border-blue-500/50 text-blue-300'
                    : 'bg-slate-900/50 border border-slate-700/30 text-slate-400 hover:text-slate-300'
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          <div className="flex gap-2 flex-wrap">
            <span className="text-xs font-semibold text-slate-400 self-center">Priority:</span>
            {(['All', 'P0', 'P1', 'P2', 'P3'] as const).map((priority) => (
              <button
                key={priority}
                onClick={() => setPriorityFilter(priority)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  priorityFilter === priority
                    ? 'bg-blue-500/30 border border-blue-500/50 text-blue-300'
                    : 'bg-slate-900/50 border border-slate-700/30 text-slate-400 hover:text-slate-300'
                }`}
              >
                {priority}
              </button>
            ))}
          </div>
        </div>

        {/* Tasks List */}
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className={`border rounded-lg transition-all ${getStatusColor(task.status)}`}
            >
              {/* Header Row */}
              <div
                className="p-4 cursor-pointer hover:bg-slate-900/50 transition-colors"
                onClick={() => toggleTask(task.id)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    <Checkbox
                      checked={completedTasks.has(task.id)}
                      onChange={() => toggleTaskComplete(task.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1 flex-shrink-0"
                    />
                    <ChevronDown
                      className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 mt-0.5 ${
                        expandedTasks[task.id] ? 'rotate-180' : ''
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-semibold ${completedTasks.has(task.id) ? 'line-through text-slate-500' : 'text-white'}`}>
                        {task.title}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">{task.framework}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    {getStatusIcon(task.status)}
                    <Badge variant={getStatusBadgeVariant(task.status)}>
                      {task.status}
                    </Badge>
                    <Badge className={getPriorityColor(task.priority)}>
                      {task.priority}
                    </Badge>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-3 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
                    style={{ width: `${task.progressPercentage}%` }}
                  ></div>
                </div>
              </div>

              {/* Expanded Details */}
              {expandedTasks[task.id] && (
                <div className="border-t border-slate-700/30 p-4 bg-slate-900/20 space-y-4">
                  {/* Description */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 mb-2">DESCRIPTION</h4>
                    <p className="text-sm text-slate-300">{task.description}</p>
                  </div>

                  {/* Meta Information */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {/* Assigned To */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <User className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">ASSIGNED TO</p>
                      </div>
                      <p className="text-sm text-white">{task.assignedTo}</p>
                      {task.assignedEmail && (
                        <p className="text-xs text-slate-500">{task.assignedEmail}</p>
                      )}
                    </div>

                    {/* Due Date */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">DUE DATE</p>
                      </div>
                      <p className="text-sm text-white">{new Date(task.dueDate).toLocaleDateString()}</p>
                      <p className={`text-xs mt-1 font-medium ${getDeadlineStatus(task.dueDate).color}`}>
                        {getDeadlineStatus(task.dueDate).text}
                      </p>
                    </div>

                    {/* Progress */}
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-slate-400" />
                        <p className="text-xs font-semibold text-slate-400">PROGRESS</p>
                      </div>
                      <p className="text-sm text-white">{task.progressPercentage}% complete</p>
                    </div>
                  </div>

                  {/* Notes */}
                  {task.notes && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 mb-2">NOTES</h4>
                      <p className="text-sm text-slate-300">{task.notes}</p>
                    </div>
                  )}

                  {/* Deliverables */}
                  {task.deliverables && task.deliverables.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 mb-2">DELIVERABLES</h4>
                      <ul className="space-y-1">
                        {task.deliverables.map((deliverable, i) => (
                          <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
                            {deliverable}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2 border-t border-slate-700/30">
                    <Button size="sm" variant="outline" className="flex-1">
                      View Details
                    </Button>
                    {task.status !== 'Completed' && (
                      <Button size="sm" variant="primary" className="flex-1">
                        Update Progress
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTasks.length === 0 && (
          <div className="text-center py-8">
            <p className="text-slate-400">No tasks match the selected filters</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
