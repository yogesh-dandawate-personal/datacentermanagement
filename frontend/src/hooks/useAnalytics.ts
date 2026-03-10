/**
 * useAnalytics Hook
 * Custom hook for analytics data fetching and state management
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import type {
  AnalyticsTrend,
  EnergyPattern,
  ForecastData,
  SustainabilityScore,
} from '../services/api'

interface UseAnalyticsReturn {
  trends: AnalyticsTrend[]
  patterns: EnergyPattern[]
  forecast: ForecastData | null
  sustainabilityScore: SustainabilityScore | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  exportAnalytics: (format: 'pdf' | 'csv') => Promise<void>
}

export function useAnalytics(
  months: number = 12,
  facilityId?: string,
  days: number = 30
): UseAnalyticsReturn {
  const [trends, setTrends] = useState<AnalyticsTrend[]>([])
  const [patterns, setPatterns] = useState<EnergyPattern[]>([])
  const [forecast, setForecast] = useState<ForecastData | null>(null)
  const [sustainabilityScore, setSustainabilityScore] = useState<SustainabilityScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [trendsData, patternsData, forecastData, scoreData] = await Promise.all([
        api.getAnalyticsTrends(months),
        api.getEnergyPatterns(facilityId, days),
        api.getForecast(6),
        api.getSustainabilityScore(),
      ])

      setTrends(trendsData)
      setPatterns(patternsData)
      setForecast(forecastData)
      setSustainabilityScore(scoreData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch analytics data')
      console.error('Analytics fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [months, facilityId, days])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const exportAnalytics = useCallback(async (format: 'pdf' | 'csv' = 'pdf') => {
    try {
      const blob = await api.exportAnalytics(format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics_report_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      console.error('Export error:', err)
      throw new Error('Failed to export analytics')
    }
  }, [])

  return {
    trends,
    patterns,
    forecast,
    sustainabilityScore,
    loading,
    error,
    refetch: fetchData,
    exportAnalytics,
  }
}

/**
 * useEmissionsTrends Hook
 * Focused hook for emissions trend data
 */
export function useEmissionsTrends(months: number = 12) {
  const [trends, setTrends] = useState<AnalyticsTrend[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTrends = async () => {
      setLoading(true)
      setError(null)

      try {
        const data = await api.getAnalyticsTrends(months)
        setTrends(data)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch emissions trends')
      } finally {
        setLoading(false)
      }
    }

    fetchTrends()
  }, [months])

  return { trends, loading, error }
}

/**
 * useEnergyPatterns Hook
 * Focused hook for energy pattern analysis
 */
export function useEnergyPatterns(facilityId?: string, days: number = 30) {
  const [patterns, setPatterns] = useState<EnergyPattern[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPatterns = async () => {
      setLoading(true)
      setError(null)

      try {
        const data = await api.getEnergyPatterns(facilityId, days)
        setPatterns(data)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch energy patterns')
      } finally {
        setLoading(false)
      }
    }

    fetchPatterns()
  }, [facilityId, days])

  return { patterns, loading, error }
}

/**
 * useForecast Hook
 * Focused hook for forecast data
 */
export function useForecast(months: number = 6) {
  const [forecast, setForecast] = useState<ForecastData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchForecast = async () => {
      setLoading(true)
      setError(null)

      try {
        const data = await api.getForecast(months)
        setForecast(data)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch forecast')
      } finally {
        setLoading(false)
      }
    }

    fetchForecast()
  }, [months])

  return { forecast, loading, error }
}

/**
 * useSustainabilityScore Hook
 * Focused hook for sustainability score
 */
export function useSustainabilityScore() {
  const [score, setScore] = useState<SustainabilityScore | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getSustainabilityScore()
      setScore(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch sustainability score')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { score, loading, error, refetch }
}
