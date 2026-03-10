/**
 * Custom hooks for Compliance Dashboard
 * Handles data fetching for compliance-related endpoints
 */

import { useState, useEffect, useCallback } from 'react'
import {
  ComplianceScore,
  ComplianceStatusSummary,
  ComplianceMatrix,
  ComplianceGap,
  RemediationTask,
  TargetTrackingData,
  AuditTrailEntry,
  Framework,
  KPITarget,
} from '../types/compliance'

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
}

/**
 * Hook to fetch overall compliance status
 */
export function useComplianceStatus(): UseApiState<ComplianceStatusSummary> {
  const [data, setData] = useState<ComplianceStatusSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Mock data - replace with actual API call
      const mockData: ComplianceStatusSummary = {
        overallStatus: 'At Risk',
        scorePercentage: 72,
        requiredMetricsCount: 45,
        submittedMetricsCount: 32,
        gapCount: 8,
        criticalGapCount: 2,
        pendingTasksCount: 15,
        overdueTasks: 3,
        frameworks: {
          gri: { status: 'On Track', score: 78 },
          tcfd: { status: 'At Risk', score: 68 },
          cdp: { status: 'At Risk', score: 70 },
        },
      }
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch compliance score trends
 */
export function useComplianceScore(): UseApiState<ComplianceScore> {
  const [data, setData] = useState<ComplianceScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: ComplianceScore = {
        overallScore: 72,
        griScore: 78,
        tcfdScore: 68,
        cdpScore: 70,
        lastUpdated: new Date().toISOString(),
        trend: [
          { date: '2025-01', overallScore: 65, griScore: 70, tcfdScore: 60, cdpScore: 65 },
          { date: '2025-02', overallScore: 68, griScore: 72, tcfdScore: 64, cdpScore: 68 },
          { date: '2025-03', overallScore: 70, griScore: 75, tcfdScore: 66, cdpScore: 69 },
          { date: '2025-04', overallScore: 72, griScore: 78, tcfdScore: 68, cdpScore: 70 },
        ],
      }
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch compliance matrix for a specific framework
 */
export function useComplianceMatrix(framework: Framework): UseApiState<ComplianceMatrix> {
  const [data, setData] = useState<ComplianceMatrix | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      // Mock data based on framework
      const mockRequirements = {
        gri: 18,
        tcfd: 15,
        cdp: 12,
      }

      const total = mockRequirements[framework.toLowerCase() as keyof typeof mockRequirements] || 15
      const complete = Math.floor(total * 0.65)
      const inProgress = Math.floor(total * 0.25)
      const notStarted = total - complete - inProgress

      const mockData: ComplianceMatrix = {
        framework,
        totalRequirements: total,
        complete,
        inProgress,
        notStarted,
        completionPercentage: Math.round((complete / total) * 100),
        requirements: Array.from({ length: total }, (_, i) => ({
          id: `${framework}-req-${i + 1}`,
          framework,
          code: `${framework}-${i + 1}`,
          title: `Requirement ${i + 1}: ${framework} Compliance Measure`,
          description: `Description of ${framework} requirement ${i + 1}`,
          status: i < complete ? 'Complete' : i < complete + inProgress ? 'In Progress' : 'Not Started',
          completionPercentage: i < complete ? 100 : i < complete + inProgress ? 60 : 0,
          lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
          evidence: i < complete ? ['evidence-1', 'evidence-2'] : undefined,
        })),
      }
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [framework])

  useEffect(() => {
    refetch()
  }, [refetch, framework])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch compliance gaps
 */
export function useComplianceGaps(): UseApiState<ComplianceGap[]> {
  const [data, setData] = useState<ComplianceGap[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: ComplianceGap[] = [
        {
          id: 'gap-1',
          framework: 'TCFD',
          requirement: 'Climate Risk Assessment',
          gapDescription: 'Missing comprehensive climate scenario analysis for 2°C and 4°C scenarios',
          severity: 'Critical',
          identifiedDate: '2025-01-15',
          targetRemediationDate: '2025-06-30',
          owner: 'John Smith',
          ownerEmail: 'john.smith@company.com',
          relatedTasks: ['task-1', 'task-2'],
        },
        {
          id: 'gap-2',
          framework: 'GRI',
          requirement: 'Energy Management System',
          gapDescription: 'Incomplete documentation of energy management procedures',
          severity: 'High',
          identifiedDate: '2025-02-01',
          targetRemediationDate: '2025-05-15',
          owner: 'Jane Doe',
          ownerEmail: 'jane.doe@company.com',
          relatedTasks: ['task-3'],
        },
        {
          id: 'gap-3',
          framework: 'CDP',
          requirement: 'Water Risk Management',
          gapDescription: 'Insufficient water stress assessment for operating locations',
          severity: 'High',
          identifiedDate: '2025-02-10',
          targetRemediationDate: '2025-07-01',
          owner: 'Mike Johnson',
          ownerEmail: 'mike.johnson@company.com',
          relatedTasks: ['task-4', 'task-5'],
        },
        {
          id: 'gap-4',
          framework: 'GRI',
          requirement: 'Waste Management Reporting',
          gapDescription: 'Missing detailed waste categorization and tracking',
          severity: 'Medium',
          identifiedDate: '2025-02-20',
          targetRemediationDate: '2025-06-15',
          owner: 'Sarah Wilson',
          ownerEmail: 'sarah.wilson@company.com',
          relatedTasks: ['task-6'],
        },
      ]
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch remediation tasks
 */
export function useRemediationTasks(): UseApiState<RemediationTask[]> {
  const [data, setData] = useState<RemediationTask[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: RemediationTask[] = [
        {
          id: 'task-1',
          title: 'Conduct Climate Scenario Analysis',
          description: 'Perform detailed climate risk analysis under 2°C and 4°C scenarios',
          gapId: 'gap-1',
          framework: 'TCFD',
          status: 'In Progress',
          priority: 'P0',
          assignedTo: 'John Smith',
          assignedEmail: 'john.smith@company.com',
          createdDate: '2025-02-01',
          dueDate: '2025-05-30',
          progressPercentage: 45,
        },
        {
          id: 'task-2',
          title: 'Document Climate Risk Mitigation Strategy',
          description: 'Create comprehensive documentation of climate risk mitigation strategies',
          gapId: 'gap-1',
          framework: 'TCFD',
          status: 'Assigned',
          priority: 'P0',
          assignedTo: 'John Smith',
          assignedEmail: 'john.smith@company.com',
          createdDate: '2025-02-15',
          dueDate: '2025-06-15',
          progressPercentage: 0,
        },
        {
          id: 'task-3',
          title: 'Update Energy Management Procedures',
          description: 'Revise and document energy management system procedures',
          gapId: 'gap-2',
          framework: 'GRI',
          status: 'In Progress',
          priority: 'P1',
          assignedTo: 'Jane Doe',
          assignedEmail: 'jane.doe@company.com',
          createdDate: '2025-02-05',
          dueDate: '2025-04-30',
          progressPercentage: 70,
        },
        {
          id: 'task-4',
          title: 'Conduct Water Stress Assessment',
          description: 'Assess water stress levels at all operating facilities',
          gapId: 'gap-3',
          framework: 'CDP',
          status: 'Assigned',
          priority: 'P1',
          assignedTo: 'Mike Johnson',
          assignedEmail: 'mike.johnson@company.com',
          createdDate: '2025-02-20',
          dueDate: '2025-06-01',
          progressPercentage: 0,
        },
        {
          id: 'task-5',
          title: 'Develop Water Management Plan',
          description: 'Create comprehensive water management and conservation plan',
          gapId: 'gap-3',
          framework: 'CDP',
          status: 'Assigned',
          priority: 'P1',
          assignedTo: 'Mike Johnson',
          assignedEmail: 'mike.johnson@company.com',
          createdDate: '2025-02-25',
          dueDate: '2025-06-30',
          progressPercentage: 0,
        },
        {
          id: 'task-6',
          title: 'Implement Waste Tracking System',
          description: 'Deploy waste categorization and tracking system',
          gapId: 'gap-4',
          framework: 'GRI',
          status: 'In Progress',
          priority: 'P2',
          assignedTo: 'Sarah Wilson',
          assignedEmail: 'sarah.wilson@company.com',
          createdDate: '2025-03-01',
          dueDate: '2025-05-31',
          progressPercentage: 35,
        },
      ]
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch target tracking data
 */
export function useTargetTracking(): UseApiState<TargetTrackingData[]> {
  const [data, setData] = useState<TargetTrackingData[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: TargetTrackingData[] = [
        {
          id: 'target-1',
          name: 'Emissions Reduction Target',
          framework: 'TCFD',
          targetValue: 50,
          targetUnit: '%',
          currentValue: 28,
          targetDate: '2030-12-31',
          startDate: '2020-01-01',
          progressPercentage: 56,
          trend: [
            { date: '2020-01', value: 0, forecast: 0 },
            { date: '2021-01', value: 8, forecast: 5 },
            { date: '2022-01', value: 15, forecast: 12 },
            { date: '2023-01', value: 20, forecast: 20 },
            { date: '2024-01', value: 25, forecast: 28 },
            { date: '2025-03', value: 28, forecast: 35 },
            { date: '2026-01', value: null as any, forecast: 40 },
            { date: '2027-01', value: null as any, forecast: 45 },
            { date: '2030-01', value: null as any, forecast: 50 },
          ],
        },
        {
          id: 'target-2',
          name: 'Renewable Energy Target',
          framework: 'GRI',
          targetValue: 80,
          targetUnit: '%',
          currentValue: 45,
          targetDate: '2030-12-31',
          startDate: '2020-01-01',
          progressPercentage: 56,
          trend: [
            { date: '2020-01', value: 15, forecast: 15 },
            { date: '2021-01', value: 22, forecast: 20 },
            { date: '2022-01', value: 30, forecast: 30 },
            { date: '2023-01', value: 35, forecast: 38 },
            { date: '2024-01', value: 42, forecast: 45 },
            { date: '2025-03', value: 45, forecast: 52 },
            { date: '2026-01', value: null as any, forecast: 60 },
            { date: '2030-01', value: null as any, forecast: 80 },
          ],
        },
        {
          id: 'target-3',
          name: 'Water Usage Reduction',
          framework: 'CDP',
          targetValue: 40,
          targetUnit: '%',
          currentValue: 12,
          targetDate: '2030-12-31',
          startDate: '2020-01-01',
          progressPercentage: 30,
          trend: [
            { date: '2020-01', value: 0, forecast: 0 },
            { date: '2022-01', value: 3, forecast: 4 },
            { date: '2023-01', value: 6, forecast: 8 },
            { date: '2024-01', value: 9, forecast: 12 },
            { date: '2025-03', value: 12, forecast: 16 },
            { date: '2026-01', value: null as any, forecast: 22 },
            { date: '2030-01', value: null as any, forecast: 40 },
          ],
        },
      ]
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch KPI targets
 */
export function useKPITargets(): UseApiState<KPITarget[]> {
  const [data, setData] = useState<KPITarget[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: KPITarget[] = [
        {
          kpiName: 'Power Usage Effectiveness',
          kpiCode: 'PUE',
          targetValue: 1.2,
          targetUnit: 'ratio',
          standardValue: 1.5,
          currentValue: 1.35,
          currentDate: new Date().toISOString(),
          progress: 56,
          status: 'On Track',
          historicalData: [
            { date: '2024-01', value: 1.55 },
            { date: '2024-06', value: 1.45 },
            { date: '2024-12', value: 1.38 },
            { date: '2025-03', value: 1.35 },
          ],
          forecastedValue: 1.25,
          forecastDate: '2025-12-31',
        },
        {
          kpiName: 'Carbon Usage Effectiveness',
          kpiCode: 'CUE',
          targetValue: 40,
          targetUnit: 'g CO₂/kWh',
          standardValue: 60,
          currentValue: 48,
          currentDate: new Date().toISOString(),
          progress: 75,
          status: 'On Track',
          historicalData: [
            { date: '2024-01', value: 65 },
            { date: '2024-06', value: 55 },
            { date: '2024-12', value: 50 },
            { date: '2025-03', value: 48 },
          ],
          forecastedValue: 42,
          forecastDate: '2025-12-31',
        },
        {
          kpiName: 'Water Usage Effectiveness',
          kpiCode: 'WUE',
          targetValue: 1.5,
          targetUnit: 'L/kWh',
          standardValue: 2.5,
          currentValue: 2.0,
          currentDate: new Date().toISOString(),
          progress: 40,
          status: 'At Risk',
          historicalData: [
            { date: '2024-01', value: 2.3 },
            { date: '2024-06', value: 2.15 },
            { date: '2024-12', value: 2.05 },
            { date: '2025-03', value: 2.0 },
          ],
          forecastedValue: 1.8,
          forecastDate: '2025-12-31',
        },
        {
          kpiName: 'Energy Reuse Effectiveness',
          kpiCode: 'ERE',
          targetValue: 2.0,
          targetUnit: 'ratio',
          standardValue: 1.0,
          currentValue: 1.65,
          currentDate: new Date().toISOString(),
          progress: 33,
          status: 'Behind',
          historicalData: [
            { date: '2024-01', value: 1.2 },
            { date: '2024-06', value: 1.35 },
            { date: '2024-12', value: 1.55 },
            { date: '2025-03', value: 1.65 },
          ],
          forecastedValue: 1.9,
          forecastDate: '2025-12-31',
        },
      ]
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook to fetch audit trail
 */
export function useAuditTrail(): UseApiState<AuditTrailEntry[]> {
  const [data, setData] = useState<AuditTrailEntry[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const mockData: AuditTrailEntry[] = [
        {
          id: 'audit-1',
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          eventType: 'requirement_updated',
          description: 'GRI-15 requirement status updated to In Progress',
          changedBy: 'Jane Doe',
          changedByEmail: 'jane.doe@company.com',
          requirementId: 'gri-req-15',
          previousValue: 'Not Started',
          newValue: 'In Progress',
        },
        {
          id: 'audit-2',
          timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          eventType: 'gap_added',
          description: 'New critical gap identified: Climate Risk Assessment',
          changedBy: 'John Smith',
          changedByEmail: 'john.smith@company.com',
          gapId: 'gap-1',
        },
        {
          id: 'audit-3',
          timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          eventType: 'task_completed',
          description: 'Task completed: Baseline Energy Assessment',
          changedBy: 'Mike Johnson',
          changedByEmail: 'mike.johnson@company.com',
          taskId: 'task-10',
        },
        {
          id: 'audit-4',
          timestamp: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          eventType: 'evidence_added',
          description: 'Evidence document added: Energy Audit Report 2025',
          changedBy: 'Sarah Wilson',
          changedByEmail: 'sarah.wilson@company.com',
          requirementId: 'gri-req-5',
        },
        {
          id: 'audit-5',
          timestamp: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
          eventType: 'status_changed',
          description: 'Overall compliance status changed from On Track to At Risk',
          changedBy: 'Admin',
          previousValue: 'On Track',
          newValue: 'At Risk',
        },
      ]
      setData(mockData)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}
