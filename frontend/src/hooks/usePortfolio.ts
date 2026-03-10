/**
 * usePortfolio Hook
 * State management and API integration for portfolio features
 */

import { useState, useCallback, useEffect } from 'react'
import { api } from '../services/api'
import type {
  CreditBatch,
  PortfolioSummary,
  RetirementRecord,
  AllocationData,
  PerformanceMetrics,
  RebalanceRecommendation,
  CreateBatchRequest,
  CreateBatchResponse,
  RetireCreditsRequest,
  RetireCreditsResponse,
  UsePortfolioReturn,
} from '../types/marketplace'

export function usePortfolio(organizationId?: string): UsePortfolioReturn {
  const [batches, setBatches] = useState<CreditBatch[]>([])
  const [summary, setSummary] = useState<PortfolioSummary | null>(null)
  const [retirements, setRetirements] = useState<RetirementRecord[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [allocations, setAllocations] = useState<AllocationData[]>([])
  const [performance, setPerformance] = useState<PerformanceMetrics | null>(null)
  const [recommendations, setRecommendations] = useState<RebalanceRecommendation[]>([])

  /**
   * Fetch credit batches
   */
  const fetchBatches = useCallback(async () => {
    if (!organizationId) {
      setError('Organization ID required')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await api.get<{ count: number; credits: any[] }>(
        `/organizations/${organizationId}/credits?status=active`
      )

      // Transform to CreditBatch format
      const transformedBatches: CreditBatch[] = response.credits.map((credit: any) => ({
        id: credit.id,
        organization_id: credit.organization_id,
        tenant_id: credit.tenant_id,
        batch_name: credit.batch_name || `Batch ${credit.batch_id}`,
        total_credits: credit.quantity,
        credits_remaining: credit.quantity_remaining || credit.quantity,
        quality_score: credit.quality_score || 100,
        description: credit.description,
        vintage_year: credit.vintage_year,
        status: credit.status,
        created_at: credit.created_at,
        updated_at: credit.updated_at || credit.created_at,
        value: (credit.quantity_remaining || credit.quantity) * 35.5, // Estimated value
      }))

      setBatches(transformedBatches)

      // Calculate summary
      calculateSummary(transformedBatches)

      // Calculate allocations
      calculateAllocations()
    } catch (err: any) {
      setError(err.message || 'Failed to fetch batches')
      console.error('Error fetching batches:', err)
    } finally {
      setIsLoading(false)
    }
  }, [organizationId])

  /**
   * Create new credit batch
   */
  const createBatch = useCallback(
    async (data: CreateBatchRequest): Promise<CreateBatchResponse> => {
      if (!organizationId) {
        throw new Error('Organization ID required')
      }

      setError(null)

      try {
        const queryParams = new URLSearchParams({
          batch_name: data.batch_name,
          total_quantity: String(data.total_quantity),
          vintage_year: String(data.vintage_year),
          credit_type: data.credit_type || 'verified',
          quality_score: String(data.quality_score || 100),
        })

        if (data.description) {
          queryParams.set('description', data.description)
        }

        const response = await api.post<CreateBatchResponse>(
          `/organizations/${organizationId}/credits/create-batch?${queryParams.toString()}`,
          {}
        )

        // Refresh batches after creation
        await fetchBatches()

        return response
      } catch (err: any) {
        const errorMsg = err.message || 'Failed to create batch'
        setError(errorMsg)
        throw new Error(errorMsg)
      }
    },
    [organizationId, fetchBatches]
  )

  /**
   * Retire credits
   */
  const retireCredits = useCallback(
    async (batchId: string, data: RetireCreditsRequest): Promise<RetireCreditsResponse> => {
      if (!organizationId) {
        throw new Error('Organization ID required')
      }

      setError(null)

      try {
        const queryParams = new URLSearchParams({
          quantity: String(data.quantity),
        })

        if (data.reason) {
          queryParams.set('reason', data.reason)
        }

        const response = await api.post<RetireCreditsResponse>(
          `/organizations/${organizationId}/credits/${batchId}/retire?${queryParams.toString()}`,
          {}
        )

        // Refresh batches after retirement
        await fetchBatches()

        // Add to retirements list
        const newRetirement: RetirementRecord = {
          id: response.id,
          organization_id: organizationId,
          tenant_id: '',
          batch_id: batchId,
          retired_credits: response.retired_credits,
          retirement_reason: response.reason,
          retirement_date: response.retirement_date,
          created_at: new Date().toISOString(),
        }
        setRetirements((prev) => [newRetirement, ...prev])

        return response
      } catch (err: any) {
        const errorMsg = err.message || 'Failed to retire credits'
        setError(errorMsg)
        throw new Error(errorMsg)
      }
    },
    [organizationId, fetchBatches]
  )

  /**
   * Calculate portfolio summary
   */
  const calculateSummary = useCallback((batchList: CreditBatch[]) => {
    const totalCredits = batchList.reduce((sum, b) => sum + b.credits_remaining, 0)
    const totalValue = batchList.reduce((sum, b) => sum + (b.value || 0), 0)
    const activeBatches = batchList.filter((b) => b.status === 'active').length
    const avgQuality =
      batchList.length > 0
        ? batchList.reduce((sum, b) => sum + b.quality_score, 0) / batchList.length
        : 0

    const portfolioSummary: PortfolioSummary = {
      total_credits: totalCredits,
      total_value: totalValue,
      active_batches: activeBatches,
      retired_credits: 0, // Will be populated from retirements
      traded_credits: 0,
      avg_quality_score: avgQuality,
      monthly_change_percent: 5.2, // Mock data
      value_trend: [
        { month: 'Jan', value: 24000 },
        { month: 'Feb', value: 26500 },
        { month: 'Mar', value: totalValue },
      ],
    }

    setSummary(portfolioSummary)
  }, [])

  /**
   * Calculate allocation by vintage year
   */
  const calculateAllocations = useCallback(() => {
    const allocationMap = new Map<number, AllocationData>()

    batches.forEach((batch) => {
      const existing = allocationMap.get(batch.vintage_year) || {
        vintage_year: batch.vintage_year,
        credits: 0,
        percentage: 0,
        value: 0,
      }

      allocationMap.set(batch.vintage_year, {
        vintage_year: batch.vintage_year,
        credits: existing.credits + batch.credits_remaining,
        percentage: 0, // Will calculate after totals
        value: existing.value + (batch.value || 0),
      })
    })

    const totalCredits = batches.reduce((sum, b) => sum + b.credits_remaining, 0)
    const allocationsArray = Array.from(allocationMap.values()).map((alloc) => ({
      ...alloc,
      percentage: totalCredits > 0 ? (alloc.credits / totalCredits) * 100 : 0,
    }))

    setAllocations(allocationsArray)
  }, [batches])

  /**
   * Fetch performance metrics
   */
  const fetchPerformance = useCallback(async () => {
    // Mock performance data
    const performanceData: PerformanceMetrics = {
      period: 'YTD',
      total_return: 12500,
      total_return_percent: 15.2,
      realized_gains: 8000,
      unrealized_gains: 4500,
      roi: 18.5,
      avg_holding_period_days: 45,
    }

    setPerformance(performanceData)
  }, [])

  // Auto-fetch batches on mount
  useEffect(() => {
    if (organizationId) {
      fetchBatches()
    }
  }, [organizationId, fetchBatches])

  return {
    // State
    batches,
    summary,
    retirements,
    isLoading,
    error,

    // Actions
    fetchBatches,
    createBatch,
    retireCredits,

    // Analytics
    allocations,
    performance,
    recommendations,
    calculateAllocations,
    fetchPerformance,
  }
}
