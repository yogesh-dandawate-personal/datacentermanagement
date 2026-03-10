/**
 * useAlerts Hook
 * Custom hook for alert management and notification preferences
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import type {
  AlertItem,
  AlertSettings,
  AlertRule,
  CreateAlertRule,
} from '../services/api'

interface UseAlertsReturn {
  alerts: AlertItem[]
  alertHistory: AlertItem[]
  settings: AlertSettings | null
  rules: AlertRule[]
  loading: boolean
  error: string | null
  dismissAlert: (id: string) => Promise<void>
  snoozeAlert: (id: string, minutes: number) => Promise<void>
  updateSettings: (data: Partial<AlertSettings>) => Promise<void>
  createRule: (data: CreateAlertRule) => Promise<AlertRule>
  updateRule: (id: string, data: Partial<AlertRule>) => Promise<void>
  deleteRule: (id: string) => Promise<void>
  refetch: () => Promise<void>
}

export function useAlerts(status?: 'active' | 'dismissed' | 'snoozed'): UseAlertsReturn {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [alertHistory, setAlertHistory] = useState<AlertItem[]>([])
  const [settings, setSettings] = useState<AlertSettings | null>(null)
  const [rules, setRules] = useState<AlertRule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [alertsData, historyData, settingsData, rulesData] = await Promise.all([
        api.getAlerts(status),
        api.getAlertHistory(50),
        api.getAlertSettings(),
        api.getAlertRules(),
      ])

      setAlerts(alertsData)
      setAlertHistory(historyData)
      setSettings(settingsData)
      setRules(rulesData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alert data')
      console.error('Alerts fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [status])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const dismissAlert = useCallback(async (id: string) => {
    await api.dismissAlert(id)
    setAlerts((prev) => prev.filter((alert) => alert.id !== id))
  }, [])

  const snoozeAlert = useCallback(async (id: string, minutes: number) => {
    await api.snoozeAlert(id, minutes)
    setAlerts((prev) => prev.map((alert) =>
      alert.id === id
        ? {
            ...alert,
            status: 'snoozed' as const,
            snoozed_until: new Date(Date.now() + minutes * 60000).toISOString(),
          }
        : alert
    ))
  }, [])

  const updateSettings = useCallback(async (data: Partial<AlertSettings>) => {
    const updated = await api.updateAlertSettings(data)
    setSettings(updated)
  }, [])

  const createRule = useCallback(async (data: CreateAlertRule) => {
    const rule = await api.createAlertRule(data)
    setRules((prev) => [...prev, rule])
    return rule
  }, [])

  const updateRule = useCallback(async (id: string, data: Partial<AlertRule>) => {
    const updated = await api.updateAlertRule(id, data)
    setRules((prev) => prev.map((r) => (r.id === id ? updated : r)))
  }, [])

  const deleteRule = useCallback(async (id: string) => {
    await api.deleteAlertRule(id)
    setRules((prev) => prev.filter((r) => r.id !== id))
  }, [])

  return {
    alerts,
    alertHistory,
    settings,
    rules,
    loading,
    error,
    dismissAlert,
    snoozeAlert,
    updateSettings,
    createRule,
    updateRule,
    deleteRule,
    refetch: fetchData,
  }
}

/**
 * useActiveAlerts Hook
 * Focused hook for active alerts only
 */
export function useActiveAlerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchAlerts = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getAlerts('active')
      setAlerts(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch active alerts')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAlerts()

    // Poll for new alerts every 30 seconds
    const interval = setInterval(fetchAlerts, 30000)

    return () => clearInterval(interval)
  }, [fetchAlerts])

  return { alerts, loading, error, refetch: fetchAlerts }
}

/**
 * useAlertSettings Hook
 * Focused hook for alert notification settings
 */
export function useAlertSettings() {
  const [settings, setSettings] = useState<AlertSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSettings = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getAlertSettings()
      setSettings(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alert settings')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  const updateSettings = useCallback(async (data: Partial<AlertSettings>) => {
    const updated = await api.updateAlertSettings(data)
    setSettings(updated)
  }, [])

  return { settings, loading, error, updateSettings, refetch: fetchSettings }
}

/**
 * useAlertRules Hook
 * Focused hook for alert rule management
 */
export function useAlertRules() {
  const [rules, setRules] = useState<AlertRule[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchRules = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getAlertRules()
      setRules(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch alert rules')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchRules()
  }, [fetchRules])

  return { rules, loading, error, refetch: fetchRules }
}
