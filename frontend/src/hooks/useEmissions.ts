/**
 * Emissions Module - Custom React Hooks
 * Handles data fetching and state management for emissions features
 */

import { useState, useEffect } from 'react'
import { emissionsApi } from '@/services/emissions-api'
import { DashboardData, PortfolioData, EmissionsAlert, EmissionsTarget, IngestionLog } from '@/types/emissions'

export function useFacilityEmissions(facilityId: string, period: string = 'current_month') {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getFacilityDashboard(facilityId, period)
        setData(result)
      } catch (err: any) {
        setError(err.message || 'Failed to load facility emissions data')
      } finally {
        setLoading(false)
      }
    }

    if (facilityId) {
      fetchData()
    }
  }, [facilityId, period])

  return { data, loading, error, refetch: () => {} }
}

export function usePortfolioEmissions(orgId: string, period: string = 'current_year') {
  const [data, setData] = useState<PortfolioData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getPortfolioOverview(orgId, period)
        setData(result)
      } catch (err: any) {
        setError(err.message || 'Failed to load portfolio data')
      } finally {
        setLoading(false)
      }
    }

    if (orgId) {
      fetchData()
    }
  }, [orgId, period])

  return { data, loading, error }
}

export function useEmissionsAlerts(orgId: string, severity?: string) {
  const [alerts, setAlerts] = useState<EmissionsAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchAlerts() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getAlerts(orgId, severity)
        setAlerts(result.data || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load alerts')
      } finally {
        setLoading(false)
      }
    }

    if (orgId) {
      fetchAlerts()
    }
  }, [orgId, severity])

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await emissionsApi.acknowledgeAlert(orgId, alertId)
      // Remove from list or update status
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, status: 'acknowledged' } : a))
    } catch (err: any) {
      setError(err.message)
    }
  }

  const resolveAlert = async (alertId: string) => {
    try {
      await emissionsApi.resolveAlert(orgId, alertId)
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, status: 'resolved' } : a))
    } catch (err: any) {
      setError(err.message)
    }
  }

  return { alerts, loading, error, acknowledgeAlert, resolveAlert }
}

export function useEmissionsTargets(orgId: string) {
  const [targets, setTargets] = useState<EmissionsTarget[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTargets() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getTargets(orgId)
        setTargets(result.data || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load targets')
      } finally {
        setLoading(false)
      }
    }

    if (orgId) {
      fetchTargets()
    }
  }, [orgId])

  const createTarget = async (targetData: Partial<EmissionsTarget>) => {
    try {
      const result = await emissionsApi.createTarget(orgId, targetData)
      setTargets([...targets, result])
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return { targets, loading, error, createTarget }
}

export function useIngestionHistory(orgId: string, sourceId?: string) {
  const [history, setHistory] = useState<IngestionLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchHistory() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getIngestionHistory(orgId, sourceId)
        setHistory(result || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load ingestion history')
      } finally {
        setLoading(false)
      }
    }

    if (orgId) {
      fetchHistory()
    }
  }, [orgId, sourceId])

  return { history, loading, error }
}

export function useEmissionsSources(orgId: string, facilityId?: string) {
  const [sources, setSources] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchSources() {
      try {
        setLoading(true)
        setError(null)
        const result = await emissionsApi.getSources(orgId, facilityId)
        setSources(result.data || [])
      } catch (err: any) {
        setError(err.message || 'Failed to load sources')
      } finally {
        setLoading(false)
      }
    }

    if (orgId) {
      fetchSources()
    }
  }, [orgId, facilityId])

  const createSource = async (sourceData: any) => {
    try {
      const result = await emissionsApi.createSource(orgId, sourceData)
      setSources([...sources, result])
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    }
  }

  return { sources, loading, error, createSource }
}

export function useCalculateEmissions(orgId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const calculateScope1 = async (sourceId: string, periodStart: string, periodEnd: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await emissionsApi.calculateScope1(orgId, sourceId, periodStart, periodEnd)
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const calculateScope2 = async (sourceId: string, periodStart: string, periodEnd: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await emissionsApi.calculateScope2(orgId, sourceId, periodStart, periodEnd)
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const calculateScope3 = async (sourceId: string, periodStart: string, periodEnd: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await emissionsApi.calculateScope3(orgId, sourceId, periodStart, periodEnd)
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { calculateScope1, calculateScope2, calculateScope3, loading, error }
}

export function useActivityDataSubmission(orgId: string) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submitSingle = async (sourceId: string, timestamp: string, value: number, unit: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await emissionsApi.submitActivityData(orgId, sourceId, timestamp, value, unit)
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const uploadBatch = async (file: File, sourceId?: string) => {
    try {
      setLoading(true)
      setError(null)
      const result = await emissionsApi.uploadBatchFile(orgId, file, sourceId)
      return result
    } catch (err: any) {
      setError(err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { submitSingle, uploadBatch, loading, error }
}
