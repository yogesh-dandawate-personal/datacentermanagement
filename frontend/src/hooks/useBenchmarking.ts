/**
 * useBenchmarking Hook
 * Custom hook for benchmarking and peer comparison data
 */

import { useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'
import type {
  BenchmarkData,
  PeerComparison,
  GapAnalysisData,
  ImprovementRecommendation,
} from '../services/api'

interface UseBenchmarkingReturn {
  benchmarks: BenchmarkData | null
  peerComparison: PeerComparison | null
  gaps: GapAnalysisData[]
  recommendations: ImprovementRecommendation[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  exportBenchmarks: (format: 'pdf' | 'csv') => Promise<void>
}

export function useBenchmarking(industry?: string): UseBenchmarkingReturn {
  const [benchmarks, setBenchmarks] = useState<BenchmarkData | null>(null)
  const [peerComparison, setPeerComparison] = useState<PeerComparison | null>(null)
  const [gaps, setGaps] = useState<GapAnalysisData[]>([])
  const [recommendations, setRecommendations] = useState<ImprovementRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [benchmarkData, peerData, gapData, recData] = await Promise.all([
        api.getBenchmarks(industry),
        api.getPeerComparison(),
        api.getGapAnalysis(),
        api.getImprovementPlan(),
      ])

      setBenchmarks(benchmarkData)
      setPeerComparison(peerData)
      setGaps(gapData)
      setRecommendations(recData)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch benchmarking data')
      console.error('Benchmarking fetch error:', err)
    } finally {
      setLoading(false)
    }
  }, [industry])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const exportBenchmarks = useCallback(async (format: 'pdf' | 'csv' = 'pdf') => {
    try {
      const blob = await api.exportBenchmarks(format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `benchmarks_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err: any) {
      console.error('Export error:', err)
      throw new Error('Failed to export benchmarks')
    }
  }, [])

  return {
    benchmarks,
    peerComparison,
    gaps,
    recommendations,
    loading,
    error,
    refetch: fetchData,
    exportBenchmarks,
  }
}

/**
 * usePeerComparison Hook
 * Focused hook for peer comparison data
 */
export function usePeerComparison() {
  const [peerComparison, setPeerComparison] = useState<PeerComparison | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPeerComparison = async () => {
      setLoading(true)
      setError(null)

      try {
        const data = await api.getPeerComparison()
        setPeerComparison(data)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch peer comparison')
      } finally {
        setLoading(false)
      }
    }

    fetchPeerComparison()
  }, [])

  return { peerComparison, loading, error }
}

/**
 * useGapAnalysis Hook
 * Focused hook for gap analysis data
 */
export function useGapAnalysis() {
  const [gaps, setGaps] = useState<GapAnalysisData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchGaps = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await api.getGapAnalysis()
      setGaps(data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch gap analysis')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchGaps()
  }, [fetchGaps])

  return { gaps, loading, error, refetch: fetchGaps }
}

/**
 * useImprovementPlan Hook
 * Focused hook for improvement recommendations
 */
export function useImprovementPlan() {
  const [recommendations, setRecommendations] = useState<ImprovementRecommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true)
      setError(null)

      try {
        const data = await api.getImprovementPlan()
        setRecommendations(data)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch improvement plan')
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [])

  return { recommendations, loading, error }
}
