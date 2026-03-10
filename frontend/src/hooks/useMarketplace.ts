/**
 * useMarketplace Hook
 * State management and API integration for marketplace features
 */

import { useState, useCallback, useEffect } from 'react'
import { api } from '../services/api'
import type {
  MarketplaceListing,
  ListingFilters,
  CreateListingRequest,
  CreateListingResponse,
  MarketPriceHistory,
  MarketInsights,
  UseMarketplaceReturn,
} from '../types/marketplace'

const DEFAULT_FILTERS: ListingFilters = {
  page: 1,
  limit: 50,
  sort_by: 'date_desc',
}

export function useMarketplace(organizationId?: string): UseMarketplaceReturn {
  const [listings, setListings] = useState<MarketplaceListing[]>([])
  const [selectedListing, setSelectedListing] = useState<MarketplaceListing | null>(null)
  const [filters, setFilters] = useState<ListingFilters>(DEFAULT_FILTERS)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [priceHistory, setPriceHistory] = useState<MarketPriceHistory[]>([])
  const [marketInsights, setMarketInsights] = useState<MarketInsights | null>(null)

  /**
   * Fetch marketplace listings with filters
   */
  const fetchListings = useCallback(async (customFilters?: ListingFilters) => {
    setIsLoading(true)
    setError(null)

    try {
      const activeFilters = customFilters || filters

      const queryParams = new URLSearchParams()
      if (activeFilters.min_price) queryParams.set('min_price', String(activeFilters.min_price))
      if (activeFilters.max_price) queryParams.set('max_price', String(activeFilters.max_price))
      if (activeFilters.limit) queryParams.set('limit', String(activeFilters.limit))

      const response = await api.get<{ count: number; listings: any[] }>(
        `/marketplace/listings?${queryParams.toString()}`
      )

      // Transform API response to match frontend types
      const transformedListings: MarketplaceListing[] = response.listings.map((listing: any) => ({
        id: listing.id,
        seller_id: listing.seller_id,
        batch_id: listing.batch_id,
        tenant_id: listing.tenant_id,
        batch_name: listing.batch_name || 'Unnamed Batch',
        seller_name: listing.seller_name || 'Unknown Seller',
        quantity_available: listing.quantity_available,
        quantity_original: listing.quantity_original || listing.quantity_available,
        price_per_credit: listing.price_per_credit,
        total_value: listing.quantity_available * listing.price_per_credit,
        listing_type: listing.type || listing.listing_type,
        status: listing.status,
        minimum_bid: listing.minimum_bid,
        expires_at: listing.expires_at,
        created_at: listing.created_at,
        updated_at: listing.updated_at || listing.created_at,
        quality_score: listing.quality_score || 100,
      }))

      setListings(transformedListings)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch listings')
      console.error('Error fetching listings:', err)
    } finally {
      setIsLoading(false)
    }
  }, [filters])

  /**
   * Fetch listing by ID
   */
  const fetchListingById = useCallback(async (id: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await api.get<any>(`/marketplace/listings/${id}`)

      const listing: MarketplaceListing = {
        id: response.id,
        seller_id: response.seller_id,
        batch_id: response.batch_id || '',
        tenant_id: response.tenant_id || '',
        batch_name: response.batch_name || 'Unnamed Batch',
        seller_name: response.seller_name || 'Unknown Seller',
        quantity_available: response.quantity_available,
        quantity_original: response.quantity_original || response.quantity_available,
        price_per_credit: response.price_per_credit,
        total_value: response.total_value || response.quantity_available * response.price_per_credit,
        listing_type: response.type || response.listing_type,
        status: response.status,
        minimum_bid: response.minimum_bid,
        expires_at: response.expires_at,
        created_at: response.created_at,
        updated_at: response.updated_at || response.created_at,
        quality_score: response.quality_score || 100,
      }

      setSelectedListing(listing)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch listing details')
      console.error('Error fetching listing:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Create new marketplace listing
   */
  const createListing = useCallback(
    async (data: CreateListingRequest): Promise<CreateListingResponse> => {
      setError(null)

      try {
        if (!organizationId) {
          throw new Error('Organization ID required to create listing')
        }

        const queryParams = new URLSearchParams({
          batch_id: data.batch_id,
          quantity: String(data.quantity),
          price_per_credit: String(data.price_per_credit),
          listing_type: data.listing_type,
          expires_in_days: String(data.expires_in_days || 30),
        })

        if (data.minimum_bid) {
          queryParams.set('minimum_bid', String(data.minimum_bid))
        }

        const response = await api.post<CreateListingResponse>(
          `/organizations/${organizationId}/marketplace/listings?${queryParams.toString()}`,
          {}
        )

        // Refresh listings after creation
        await fetchListings()

        return response
      } catch (err: any) {
        const errorMsg = err.message || 'Failed to create listing'
        setError(errorMsg)
        throw new Error(errorMsg)
      }
    },
    [organizationId, fetchListings]
  )

  /**
   * Update filters
   */
  const updateFilters = useCallback((newFilters: Partial<ListingFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }))
  }, [])

  /**
   * Clear all filters
   */
  const clearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS)
  }, [])

  /**
   * Select a listing
   */
  const selectListing = useCallback((listing: MarketplaceListing | null) => {
    setSelectedListing(listing)
  }, [])

  /**
   * Fetch market insights
   */
  const fetchMarketInsights = useCallback(async () => {
    try {
      const response = await api.get<MarketInsights>('/marketplace/analytics/market-insights')
      setMarketInsights(response)
    } catch (err: any) {
      console.error('Error fetching market insights:', err)
    }
  }, [])

  /**
   * Fetch price history
   */
  const fetchPriceHistory = useCallback(async (days = 30) => {
    try {
      const response = await api.get<{ period_days: number; current_price: number; price_trend: any[] }>(
        `/marketplace/analytics/price-history?days=${days}`
      )

      const history: MarketPriceHistory[] = response.price_trend.map((point: any) => ({
        date: point.date,
        price: point.price,
        volume: point.volume,
      }))

      setPriceHistory(history)
    } catch (err: any) {
      console.error('Error fetching price history:', err)
    }
  }, [])

  // Auto-fetch listings on mount or filter change
  useEffect(() => {
    fetchListings()
  }, [fetchListings])

  return {
    // State
    listings,
    selectedListing,
    filters,
    isLoading,
    error,

    // Actions
    fetchListings,
    fetchListingById,
    createListing,
    updateFilters,
    clearFilters,
    selectListing,

    // Analytics
    priceHistory,
    marketInsights,
    fetchMarketInsights,
  }
}
