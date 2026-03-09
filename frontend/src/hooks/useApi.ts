/**
 * Custom Hooks for API Integration
 * Provides easy data fetching with loading and error states
 */

import { useState, useEffect, useCallback } from 'react'
import api, { ApiError } from '../services/api'

export interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
  refetch: () => Promise<void>
}

/**
 * Generic hook for API data fetching
 */
export function useApi<T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
): UseApiState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn()
      setData(result)
    } catch (err) {
      setError(err as ApiError)
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    refetch()
  }, dependencies)

  return { data, loading, error, refetch }
}

/**
 * Hook for energy metrics
 */
export function useEnergyMetrics(facilityId?: string, dateRange?: string) {
  return useApi(
    () => api.getEnergyMetrics(facilityId, dateRange),
    [facilityId, dateRange]
  )
}

/**
 * Hook for facilities list
 */
export function useFacilities() {
  return useApi(() => api.getFacilities(), [])
}

/**
 * Hook for single facility
 */
export function useFacility(id: string) {
  return useApi(
    () => api.getFacility(id),
    [id]
  )
}

/**
 * Hook for energy trend data
 */
export function useEnergyTrend(facilityId?: string, days?: number) {
  return useApi(
    () => api.getEnergyTrend(facilityId, days),
    [facilityId, days]
  )
}

/**
 * Hook for reports with filtering
 */
export function useReports(
  search?: string,
  type?: string,
  status?: string,
  page?: number,
  pageSize?: number
) {
  return useApi(
    () => api.getReports(search, type, status, page, pageSize),
    [search, type, status, page, pageSize]
  )
}

/**
 * Hook for compliance metrics
 */
export function useComplianceMetrics() {
  return useApi(() => api.getComplianceMetrics(), [])
}

/**
 * Hook for user profile
 */
export function useUserProfile() {
  return useApi(() => api.getUserProfile(), [])
}

/**
 * Hook for organization settings
 */
export function useOrganizationSettings() {
  return useApi(() => api.getOrganizationSettings(), [])
}

/**
 * Hook for API mutations (POST, PUT, DELETE)
 */
export interface UseMutationState<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
  execute: (fn: () => Promise<T>) => Promise<T | null>
}

export function useMutation<T>(): UseMutationState<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  const execute = useCallback(async (fn: () => Promise<T>): Promise<T | null> => {
    setLoading(true)
    setError(null)
    try {
      const result = await fn()
      setData(result)
      return result
    } catch (err) {
      const apiError = err as ApiError
      setError(apiError)
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, execute }
}

/**
 * Hook for form submission
 */
export function useFormSubmit<T>(
  onSubmit: (data: any) => Promise<T>,
  onSuccess?: (data: T) => void
) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = useCallback(
    async (formData: any) => {
      setLoading(true)
      setError(null)
      setSuccess(false)

      try {
        const result = await onSubmit(formData)
        setSuccess(true)
        onSuccess?.(result)
        return true
      } catch (err) {
        setError(err as ApiError)
        return false
      } finally {
        setLoading(false)
      }
    },
    [onSubmit, onSuccess]
  )

  return { handleSubmit, loading, error, success }
}
