/**
 * TypeScript types for Compliance Dashboard
 * Covers GRI, TCFD, and CDP frameworks
 */

export type RequirementStatus = 'Complete' | 'In Progress' | 'Not Started'
export type Framework = 'GRI' | 'TCFD' | 'CDP'
export type GapSeverity = 'Critical' | 'High' | 'Medium' | 'Low'
export type TaskStatus = 'Assigned' | 'In Progress' | 'Completed'
export type TaskPriority = 'P0' | 'P1' | 'P2' | 'P3'
export type OverallComplianceStatus = 'On Track' | 'At Risk' | 'Non-Compliant'

/**
 * Compliance Requirement
 * Represents a single requirement from a framework
 */
export interface ComplianceRequirement {
  id: string
  framework: Framework
  code: string
  title: string
  description: string
  status: RequirementStatus
  completionPercentage: number
  lastUpdated: string
  evidence?: string[] // List of evidence document IDs
  assignedTo?: string
  dueDate?: string
}

/**
 * GRI/TCFD/CDP Alignment Matrix
 * Shows compliance status across all requirements
 */
export interface ComplianceMatrix {
  framework: Framework
  totalRequirements: number
  complete: number
  inProgress: number
  notStarted: number
  completionPercentage: number
  requirements: ComplianceRequirement[]
}

/**
 * Compliance Gap
 * Represents a gap identified in compliance
 */
export interface ComplianceGap {
  id: string
  framework: Framework
  requirement: string
  gapDescription: string
  severity: GapSeverity
  identifiedDate: string
  targetRemediationDate: string
  owner: string
  ownerEmail?: string
  relatedTasks: string[] // Task IDs
  evidence?: string[]
}

/**
 * Remediation Task
 * Task required to close a compliance gap
 */
export interface RemediationTask {
  id: string
  title: string
  description: string
  gapId: string
  framework: Framework
  status: TaskStatus
  priority: TaskPriority
  assignedTo: string
  assignedEmail?: string
  createdDate: string
  dueDate: string
  completedDate?: string
  progressPercentage: number
  notes?: string
  deliverables?: string[]
}

/**
 * Target Tracking Data
 * Tracks progress towards compliance targets
 */
export interface TargetTrackingData {
  id: string
  name: string
  framework: Framework
  targetValue: number
  targetUnit: string
  currentValue: number
  targetDate: string
  startDate: string
  progressPercentage: number
  trend: Array<{
    date: string
    value: number
    forecast?: number
  }>
}

/**
 * Compliance Score
 * Overall compliance health score
 */
export interface ComplianceScore {
  overallScore: number // 0-100
  griScore: number
  tcfdScore: number
  cdpScore: number
  trend: Array<{
    date: string
    overallScore: number
    griScore: number
    tcfdScore: number
    cdpScore: number
  }>
  lastUpdated: string
}

/**
 * Compliance Status Summary
 * High-level overview of compliance status
 */
export interface ComplianceStatusSummary {
  overallStatus: OverallComplianceStatus
  scorePercentage: number
  requiredMetricsCount: number
  submittedMetricsCount: number
  gapCount: number
  criticalGapCount: number
  pendingTasksCount: number
  overdueTasks: number
  frameworks: {
    gri: { status: OverallComplianceStatus; score: number }
    tcfd: { status: OverallComplianceStatus; score: number }
    cdp: { status: OverallComplianceStatus; score: number }
  }
}

/**
 * Audit Trail Entry
 * Records changes to compliance status
 */
export interface AuditTrailEntry {
  id: string
  timestamp: string
  eventType: 'requirement_updated' | 'gap_added' | 'task_completed' | 'evidence_added' | 'status_changed'
  description: string
  changedBy: string
  changedByEmail?: string
  requirementId?: string
  gapId?: string
  taskId?: string
  previousValue?: any
  newValue?: any
  notes?: string
}

/**
 * Compliance Report
 * Generated compliance report with all details
 */
export interface ComplianceReport {
  id: string
  organizationName: string
  reportDate: string
  reportPeriod: string
  overallScore: number
  overallStatus: OverallComplianceStatus
  executiveSummary: string
  matrices: {
    gri: ComplianceMatrix
    tcfd: ComplianceMatrix
    cdp: ComplianceMatrix
  }
  gaps: ComplianceGap[]
  tasks: RemediationTask[]
  targets: TargetTrackingData[]
  preparedBy: string
  preparedByEmail?: string
  approvedBy?: string
  approvedDate?: string
  signOffDate?: string
}

/**
 * KPI Target Tracking
 * Tracks specific KPI targets (PUE, CUE, WUE, ERE)
 */
export interface KPITarget {
  kpiName: string
  kpiCode: 'PUE' | 'CUE' | 'WUE' | 'ERE'
  targetValue: number
  targetUnit: string
  standardValue: number
  currentValue: number
  currentDate: string
  progress: number
  status: 'On Track' | 'At Risk' | 'Behind'
  historicalData: Array<{
    date: string
    value: number
  }>
  forecastedValue?: number
  forecastDate?: string
}

/**
 * Evidence Document
 * Supporting document for compliance
 */
export interface EvidenceDocument {
  id: string
  name: string
  description: string
  documentType: string
  uploadDate: string
  uploadedBy: string
  requirementIds: string[]
  gapIds: string[]
  fileUrl: string
  fileSizeBytes: number
  verified: boolean
  verifiedBy?: string
  verifiedDate?: string
}
