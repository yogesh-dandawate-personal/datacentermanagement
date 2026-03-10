/**
 * Marketplace, Trading, and Portfolio TypeScript Types
 * Complete type definitions for Sprint 8 features
 */

// ============================================================================
// CARBON CREDIT TYPES
// ============================================================================

export type CreditStatus = 'active' | 'traded' | 'retired' | 'expired'
export type ListingType = 'fixed_price' | 'auction' | 'negotiable'
export type TradeStatus = 'pending' | 'completed' | 'cancelled' | 'failed'
export type PaymentStatus = 'pending' | 'confirmed' | 'failed'

export interface CarbonCredit {
  id: string
  organization_id: string
  tenant_id: string
  batch_id: string
  credit_type: string
  vintage_year: number
  quantity: number
  quantity_remaining: number
  status: CreditStatus
  quality_score: number
  created_at: string
  updated_at: string
}

export interface CreditBatch {
  id: string
  organization_id: string
  tenant_id: string
  batch_name: string
  total_credits: number
  credits_remaining: number
  quality_score: number
  description?: string
  vintage_year: number
  status: CreditStatus
  created_at: string
  updated_at: string
  value?: number
}

export interface RetirementRecord {
  id: string
  organization_id: string
  tenant_id: string
  batch_id: string
  retired_credits: number
  retirement_reason?: string
  retirement_date: string
  created_at: string
}

// ============================================================================
// MARKETPLACE LISTING TYPES
// ============================================================================

export interface MarketplaceListing {
  id: string
  seller_id: string
  batch_id: string
  tenant_id: string
  batch_name?: string
  seller_name?: string
  quantity_available: number
  quantity_original: number
  price_per_credit: number
  total_value: number
  listing_type: ListingType
  status: 'active' | 'sold' | 'expired' | 'cancelled'
  minimum_bid?: number
  expires_at?: string
  created_at: string
  updated_at: string
  quality_score?: number
}

export interface ListingFilters {
  search?: string
  min_price?: number
  max_price?: number
  listing_type?: ListingType
  seller_rating?: number
  min_quality?: number
  sort_by?: 'price_asc' | 'price_desc' | 'date_asc' | 'date_desc' | 'quality_desc'
  page?: number
  limit?: number
}

export interface ListingFormData {
  batch_id: string
  quantity: number
  price_per_credit: number
  listing_type: ListingType
  expires_in_days: number
  minimum_bid?: number
}

// ============================================================================
// TRADING TYPES
// ============================================================================

export interface Trade {
  id: string
  listing_id: string
  buyer_id: string
  seller_id: string
  batch_name?: string
  counterparty?: string
  type: 'buy' | 'sell'
  quantity: number
  price_per_credit: number
  total_price: number
  status: TradeStatus
  payment_status?: PaymentStatus
  trade_date: string
  completion_date?: string
  created_at: string
  updated_at: string
}

export interface TradeFormData {
  listing_id: string
  quantity: number
  agreed_price?: number
}

export interface TradeMetrics {
  total_trades: number
  total_volume: number
  total_spent: number
  total_earned: number
  net_position: number
  avg_buy_price: number
  avg_sell_price: number
  completed_count: number
  pending_count: number
  cancelled_count: number
}

export interface OrderBookEntry {
  price: number
  quantity: number
  type: 'buy' | 'sell'
  timestamp: string
}

// ============================================================================
// PORTFOLIO TYPES
// ============================================================================

export interface PortfolioSummary {
  total_credits: number
  total_value: number
  active_batches: number
  retired_credits: number
  traded_credits: number
  avg_quality_score: number
  monthly_change_percent: number
  value_trend: ValueTrendPoint[]
}

export interface ValueTrendPoint {
  month: string
  date?: string
  value: number
}

export interface AllocationData {
  vintage_year: number
  credits: number
  percentage: number
  value: number
}

export interface PerformanceMetrics {
  period: string
  total_return: number
  total_return_percent: number
  realized_gains: number
  unrealized_gains: number
  roi: number
  avg_holding_period_days: number
}

export interface RebalanceRecommendation {
  id: string
  type: 'buy' | 'sell' | 'retire'
  batch_id: string
  batch_name: string
  current_quantity: number
  recommended_quantity: number
  reason: string
  priority: 'high' | 'medium' | 'low'
  estimated_value: number
}

// ============================================================================
// ANALYTICS TYPES
// ============================================================================

export interface MarketPriceHistory {
  date: string
  price: number
  volume?: number
}

export interface TradingVolume {
  period: string
  date?: string
  volume: number
  trades: number
  buy_volume: number
  sell_volume: number
}

export interface MarketInsights {
  current_market_price: number
  price_change_24h: number
  price_change_7d: number
  monthly_volume: TradingVolume
  market_status: 'active' | 'inactive' | 'volatile'
  liquidity_score: number
  recommendations: string[]
}

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

export interface CreateBatchRequest {
  batch_name: string
  total_quantity: number
  credit_type?: string
  vintage_year: number
  description?: string
  quality_score?: number
}

export interface CreateBatchResponse {
  id: string
  batch_name: string
  total_credits: number
  quality_score: number
  created_at: string
}

export interface CreateListingRequest {
  batch_id: string
  quantity: number
  price_per_credit: number
  listing_type: ListingType
  expires_in_days?: number
  minimum_bid?: number
}

export interface CreateListingResponse {
  id: string
  quantity: number
  price_per_credit: number
  type: ListingType
  status: string
  expires_at?: string
}

export interface ExecuteTradeRequest {
  listing_id: string
  quantity: number
  agreed_price?: number
}

export interface ExecuteTradeResponse {
  id: string
  listing_id: string
  quantity: number
  price_per_credit: number
  total_price: number
  status: TradeStatus
  trade_date: string
}

export interface RetireCreditsRequest {
  quantity: number
  reason?: string
}

export interface RetireCreditsResponse {
  id: string
  retired_credits: number
  reason?: string
  retirement_date: string
}

export interface ListingsResponse {
  count: number
  listings: MarketplaceListing[]
  page?: number
  total_pages?: number
}

export interface TradeHistoryResponse {
  organization_id: string
  role: 'buyer' | 'seller' | 'all'
  count: number
  trades: Trade[]
}

export interface CreditsResponse {
  organization_id: string
  status: CreditStatus
  count: number
  credits: CarbonCredit[]
}

// ============================================================================
// UI STATE TYPES
// ============================================================================

export interface MarketplaceState {
  listings: MarketplaceListing[]
  selectedListing: MarketplaceListing | null
  filters: ListingFilters
  isLoading: boolean
  error: string | null
  pagination: {
    page: number
    limit: number
    total: number
    total_pages: number
  }
}

export interface TradingState {
  trades: Trade[]
  metrics: TradeMetrics | null
  orderBook: OrderBookEntry[]
  isExecuting: boolean
  error: string | null
}

export interface PortfolioState {
  batches: CreditBatch[]
  summary: PortfolioSummary | null
  retirements: RetirementRecord[]
  allocations: AllocationData[]
  performance: PerformanceMetrics | null
  recommendations: RebalanceRecommendation[]
  isLoading: boolean
  error: string | null
}

// ============================================================================
// HOOK RETURN TYPES
// ============================================================================

export interface UseMarketplaceReturn {
  // State
  listings: MarketplaceListing[]
  selectedListing: MarketplaceListing | null
  filters: ListingFilters
  isLoading: boolean
  error: string | null

  // Actions
  fetchListings: (filters?: ListingFilters) => Promise<void>
  fetchListingById: (id: string) => Promise<void>
  createListing: (data: CreateListingRequest) => Promise<CreateListingResponse>
  updateFilters: (filters: Partial<ListingFilters>) => void
  clearFilters: () => void
  selectListing: (listing: MarketplaceListing | null) => void

  // Analytics
  priceHistory: MarketPriceHistory[]
  marketInsights: MarketInsights | null
  fetchMarketInsights: () => Promise<void>
}

export interface UseTradingReturn {
  // State
  trades: Trade[]
  metrics: TradeMetrics | null
  isExecuting: boolean
  error: string | null

  // Actions
  executeTrade: (data: ExecuteTradeRequest) => Promise<ExecuteTradeResponse>
  fetchTradeHistory: (role?: 'buyer' | 'seller' | 'all') => Promise<void>
  completeTrade: (tradeId: string) => Promise<void>

  // Analytics
  calculateMetrics: (trades: Trade[]) => TradeMetrics
  monthlyVolume: TradingVolume[]
  fetchTradingVolume: (days?: number) => Promise<void>
}

export interface UsePortfolioReturn {
  // State
  batches: CreditBatch[]
  summary: PortfolioSummary | null
  retirements: RetirementRecord[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchBatches: () => Promise<void>
  createBatch: (data: CreateBatchRequest) => Promise<CreateBatchResponse>
  retireCredits: (batchId: string, data: RetireCreditsRequest) => Promise<RetireCreditsResponse>

  // Analytics
  allocations: AllocationData[]
  performance: PerformanceMetrics | null
  recommendations: RebalanceRecommendation[]
  calculateAllocations: () => void
  fetchPerformance: () => Promise<void>
}
