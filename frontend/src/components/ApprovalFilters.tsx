/**
 * Approval Filters Component
 * Provides filtering options for approval requests
 */

import { useState } from 'react'
import { Button, Input, Select, Checkbox } from './ui'
import { ApprovalStatus, ApprovalType, ApprovalFilter } from '../types/approval'
import { Search, X } from 'lucide-react'

interface ApprovalFiltersProps {
  onFilterChange: (filters: ApprovalFilter) => void
  onSortChange: (field: string, direction: string) => void
}

const statusOptions: { value: ApprovalStatus; label: string }[] = [
  { value: 'draft', label: 'Draft' },
  { value: 'under_review', label: 'Under Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
]

const typeOptions: { value: ApprovalType; label: string }[] = [
  { value: 'report', label: 'Report' },
  { value: 'calculation', label: 'Calculation' },
  { value: 'metric', label: 'Metric' },
]

export function ApprovalFilters({
  onFilterChange,
  onSortChange,
}: ApprovalFiltersProps) {
  const [search, setSearch] = useState('')
  const [selectedStatuses, setSelectedStatuses] = useState<ApprovalStatus[]>([])
  const [selectedTypes, setSelectedTypes] = useState<ApprovalType[]>([])
  const [assigneeFilter, setAssigneeFilter] = useState<'me' | 'my_team' | 'all'>(
    'all'
  )
  const [sortField, setSortField] = useState('due_date')
  const [sortDirection, setSortDirection] = useState('asc')
  const [showAdvanced, setShowAdvanced] = useState(false)

  const handleStatusToggle = (status: ApprovalStatus) => {
    const newStatuses = selectedStatuses.includes(status)
      ? selectedStatuses.filter((s) => s !== status)
      : [...selectedStatuses, status]

    setSelectedStatuses(newStatuses)
    onFilterChange({
      status: newStatuses.length > 0 ? newStatuses : undefined,
      type: selectedTypes.length > 0 ? selectedTypes : undefined,
      assignee: assigneeFilter,
      search: search || undefined,
    })
  }

  const handleTypeToggle = (type: ApprovalType) => {
    const newTypes = selectedTypes.includes(type)
      ? selectedTypes.filter((t) => t !== type)
      : [...selectedTypes, type]

    setSelectedTypes(newTypes)
    onFilterChange({
      status: selectedStatuses.length > 0 ? selectedStatuses : undefined,
      type: newTypes.length > 0 ? newTypes : undefined,
      assignee: assigneeFilter,
      search: search || undefined,
    })
  }

  const handleSearchChange = (value: string) => {
    setSearch(value)
    onFilterChange({
      status: selectedStatuses.length > 0 ? selectedStatuses : undefined,
      type: selectedTypes.length > 0 ? selectedTypes : undefined,
      assignee: assigneeFilter,
      search: value || undefined,
    })
  }

  const handleAssigneeChange = (value: 'me' | 'my_team' | 'all') => {
    setAssigneeFilter(value)
    onFilterChange({
      status: selectedStatuses.length > 0 ? selectedStatuses : undefined,
      type: selectedTypes.length > 0 ? selectedTypes : undefined,
      assignee: value,
      search: search || undefined,
    })
  }

  const handleSortChange = (field: string, direction: string) => {
    setSortField(field)
    setSortDirection(direction)
    onSortChange(field, direction)
  }

  const clearFilters = () => {
    setSearch('')
    setSelectedStatuses([])
    setSelectedTypes([])
    setAssigneeFilter('all')
    setSortField('due_date')
    setSortDirection('asc')
    onFilterChange({})
    onSortChange('due_date', 'asc')
  }

  const hasActiveFilters =
    search ||
    selectedStatuses.length > 0 ||
    selectedTypes.length > 0 ||
    assigneeFilter !== 'all'

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
        <Input
          type="text"
          placeholder="Search by name, submitter, or approval ID..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Main Filters Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Assignee Filter */}
        <Select
          label="Assignee"
          value={assigneeFilter}
          onChange={(e) =>
            handleAssigneeChange(e.target.value as 'me' | 'my_team' | 'all')
          }
          options={[
            { value: 'all', label: 'All' },
            { value: 'me', label: 'Me' },
            { value: 'my_team', label: 'My Team' },
          ]}
        />

        {/* Sort Field */}
        <Select
          label="Sort By"
          value={sortField}
          onChange={(e) => handleSortChange(e.target.value, sortDirection)}
          options={[
            { value: 'due_date', label: 'Due Date' },
            { value: 'submitted_date', label: 'Submitted Date' },
            { value: 'priority', label: 'Priority' },
            { value: 'status', label: 'Status' },
          ]}
        />

        {/* Sort Direction */}
        <Select
          label="Order"
          value={sortDirection}
          onChange={(e) => handleSortChange(sortField, e.target.value)}
          options={[
            { value: 'asc', label: 'Ascending' },
            { value: 'desc', label: 'Descending' },
          ]}
        />
      </div>

      {/* Advanced Filters Toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
      >
        {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
      </button>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="border border-slate-700/30 rounded-lg p-4 space-y-4">
          {/* Status Filter */}
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3">Status</h4>
            <div className="space-y-2">
              {statusOptions.map((option) => (
                <label key={option.value} className="flex items-center gap-2">
                  <Checkbox
                    checked={selectedStatuses.includes(option.value)}
                    onChange={() => handleStatusToggle(option.value)}
                  />
                  <span className="text-sm text-slate-300">{option.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Type Filter */}
          <div>
            <h4 className="text-sm font-medium text-slate-300 mb-3">Type</h4>
            <div className="space-y-2">
              {typeOptions.map((option) => (
                <label key={option.value} className="flex items-center gap-2">
                  <Checkbox
                    checked={selectedTypes.includes(option.value)}
                    onChange={() => handleTypeToggle(option.value)}
                  />
                  <span className="text-sm text-slate-300">{option.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
          <div className="flex items-center gap-2 flex-wrap">
            {search && (
              <span className="text-xs bg-primary-600/20 text-primary-300 px-2 py-1 rounded">
                Search: {search}
              </span>
            )}
            {selectedStatuses.map((status) => (
              <span
                key={status}
                className="text-xs bg-blue-600/20 text-blue-300 px-2 py-1 rounded"
              >
                Status: {status}
              </span>
            ))}
            {selectedTypes.map((type) => (
              <span
                key={type}
                className="text-xs bg-green-600/20 text-green-300 px-2 py-1 rounded"
              >
                Type: {type}
              </span>
            ))}
            {assigneeFilter !== 'all' && (
              <span className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded">
                Assignee: {assigneeFilter}
              </span>
            )}
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={clearFilters}
            className="text-xs"
          >
            <X className="w-3 h-3 mr-1" />
            Clear
          </Button>
        </div>
      )}
    </div>
  )
}
