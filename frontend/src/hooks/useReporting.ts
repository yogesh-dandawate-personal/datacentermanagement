/**
 * useReporting Hook
 * Custom hook for report management, scheduling, and delivery tracking
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import type {
  ReportTemplate,
  CreateReportTemplate,
  ReportSchedule,
  CreateReportSchedule,
  ReportPreview,
  DeliveryLog,
} from '../services/api'

interface UseReportingReturn {
  templates: ReportTemplate[]
  schedules: ReportSchedule[]
  deliveryLog: DeliveryLog[]
  loading: boolean
  error: string | null
  createTemplate: (data: CreateReportTemplate) => Promise<ReportTemplate>
  updateTemplate: (id: string, data: Partial<ReportTemplate>) => Promise<void>
  deleteTemplate: (id: string) => Promise<void>
  createSchedule: (data: CreateReportSchedule) => Promise<ReportSchedule>
  updateSchedule: (id: string, data: Partial<ReportSchedule>) => Promise<void>
  deleteSchedule: (id: string) => Promise<void>
  previewReport: (templateId: string, filters?: any) => Promise<ReportPreview>
  resendReport: (deliveryId: string) => Promise<void>
  refetch: () => Promise<void>
}

export function useReporting(): UseReportingReturn {
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [schedules, setSchedules] = useState<ReportSchedule[]>([])
  const [deliveryLog, setDeliveryLog] = useState<DeliveryLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [templatesData, schedulesData, logsData] = await Promise.all([
        api.getReportTemplates(),
        api.getReportSchedules(),
        api.getDeliveryLog(),
      ])

      setTemplates(templatesData)
      setSchedules(schedulesData)
      setDeliveryLog(logsData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch reporting data')
      console.error('Reporting fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const createTemplate = useCallback(async (data: CreateReportTemplate) => {
    const template = await api.createReportTemplate(data)
    setTemplates((prev) => [...prev, template])
    return template
  }, [])

  const updateTemplate = useCallback(async (id: string, data: Partial<ReportTemplate>) => {
    const updated = await api.updateReportTemplate(id, data)
    setTemplates((prev) => prev.map((t) => (t.id === id ? updated : t)))
  }, [])

  const deleteTemplate = useCallback(async (id: string) => {
    await api.deleteReportTemplate(id)
    setTemplates((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const createSchedule = useCallback(async (data: CreateReportSchedule) => {
    const schedule = await api.createReportSchedule(data)
    setSchedules((prev) => [...prev, schedule])
    return schedule
  }, [])

  const updateSchedule = useCallback(async (id: string, data: Partial<ReportSchedule>) => {
    const updated = await api.updateReportSchedule(id, data)
    setSchedules((prev) => prev.map((s) => (s.id === id ? updated : s)))
  }, [])

  const deleteSchedule = useCallback(async (id: string) => {
    await api.deleteReportSchedule(id)
    setSchedules((prev) => prev.filter((s) => s.id !== id))
  }, [])

  const previewReport = useCallback(async (templateId: string, filters?: any) => {
    return await api.previewReport(templateId, filters)
  }, [])

  const resendReport = useCallback(async (deliveryId: string) => {
    await api.resendReport(deliveryId)
    await fetchData() // Refresh delivery log
  }, [fetchData])

  return {
    templates,
    schedules,
    deliveryLog,
    loading,
    error,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    createSchedule,
    updateSchedule,
    deleteSchedule,
    previewReport,
    resendReport,
    refetch: fetchData,
  }
}

/**
 * useReportTemplates Hook
 * Focused hook for report templates
 */
export function useReportTemplates() {
  const [templates, setTemplates] = useState<ReportTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getReportTemplates()
      setTemplates(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch templates')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

  return { templates, loading, error, refetch: fetchTemplates }
}

/**
 * useReportSchedules Hook
 * Focused hook for report schedules
 */
export function useReportSchedules() {
  const [schedules, setSchedules] = useState<ReportSchedule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSchedules = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getReportSchedules()
      setSchedules(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch schedules')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSchedules()
  }, [fetchSchedules])

  return { schedules, loading, error, refetch: fetchSchedules }
}

/**
 * useDeliveryLog Hook
 * Focused hook for delivery log tracking
 */
export function useDeliveryLog(scheduleId?: string) {
  const [deliveryLog, setDeliveryLog] = useState<DeliveryLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLog = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getDeliveryLog(scheduleId)
      setDeliveryLog(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch delivery log')
    } finally {
      setLoading(false)
    }
  }, [scheduleId])

  useEffect(() => {
    fetchLog()
  }, [fetchLog])

  return { deliveryLog, loading, error, refetch: fetchLog }
}
