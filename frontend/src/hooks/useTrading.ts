/**
 * useTrading Hook
 * State management and API integration for trading features
 */

import { useState, useCallback } from 'react'
import { api } from '../services/api'
import type {
  Trade,
  TradeMetrics,
  ExecuteTradeRequest,
  ExecuteTradeResponse,
  TradingVolume,
  UseTradingReturn,
} from '../types/marketplace'

export function useTrading(organizationId?: string): UseTradingReturn {
  const [trades, setTrades] = useState<Trade[]>([])
  const [metrics, setMetrics] = useState<TradeMetrics | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [monthlyVolume, setMonthlyVolume] = useState<TradingVolume[]>([])

  /**
   * Execute a trade
   */
  const executeTrade = useCallback(
    async (data: ExecuteTradeRequest): Promise<ExecuteTradeResponse> => {
      setIsExecuting(true)
      setError(null)

      try {
        const queryParams = new URLSearchParams({
          listing_id: data.listing_id,
          quantity: String(data.quantity),
        })

        if (data.agreed_price) {
          queryParams.set('agreed_price', String(data.agreed_price))
        }

        const response = await api.post<ExecuteTradeResponse>(
          `/trades/execute?${queryParams.toString()}`,
          {}
        )

        // Refresh trade history after execution
        if (organizationId) {
          await fetchTradeHistory()
        }

        return response
      } catch (err: any) {
        const errorMsg = err.message || 'Failed to execute trade'
        setError(errorMsg)
        throw new Error(errorMsg)
      } finally {
        setIsExecuting(false)
      }
    },
    [organizationId]
  )

  /**
   * Fetch trade history
   */
  const fetchTradeHistory = useCallback(
    async (role: 'buyer' | 'seller' | 'all' = 'all') => {
      if (!organizationId) {
        setError('Organization ID required')
        return
      }

      setError(null)

      try {
        const response = await api.get<{ count: number; trades: any[] }>(
          `/organizations/${organizationId}/trades?role=${role}&limit=100`
        )

        // Transform API response
        const transformedTrades: Trade[] = response.trades.map((trade: any) => ({
          id: trade.id,
          listing_id: trade.listing_id,
          buyer_id: trade.buyer_id,
          seller_id: trade.seller_id,
          batch_name: trade.batch_name || 'Unnamed Batch',
          counterparty: trade.counterparty || 'Unknown',
          type: trade.buyer_id === organizationId ? 'buy' : 'sell',
          quantity: trade.quantity,
          price_per_credit: trade.price_per_credit,
          total_price: trade.total_price,
          status: trade.status,
          payment_status: trade.payment_status,
          trade_date: trade.trade_date,
          completion_date: trade.completion_date,
          created_at: trade.created_at,
          updated_at: trade.updated_at || trade.created_at,
        }))

        setTrades(transformedTrades)

        // Calculate metrics
        const calculatedMetrics = calculateMetrics(transformedTrades)
        setMetrics(calculatedMetrics)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch trade history')
        console.error('Error fetching trades:', err)
      }
    },
    [organizationId]
  )

  /**
   * Complete a trade
   */
  const completeTrade = useCallback(async (tradeId: string) => {
    setError(null)

    try {
      await api.post<any>(`/trades/${tradeId}/complete?payment_confirmed=true`, {})

      // Refresh trade history
      if (organizationId) {
        await fetchTradeHistory()
      }
    } catch (err: any) {
      setError(err.message || 'Failed to complete trade')
      throw err
    }
  }, [organizationId, fetchTradeHistory])

  /**
   * Calculate trade metrics
   */
  const calculateMetrics = useCallback((tradeList: Trade[]): TradeMetrics => {
    const completedTrades = tradeList.filter((t) => t.status === 'completed')
    const buyTrades = completedTrades.filter((t) => t.type === 'buy')
    const sellTrades = completedTrades.filter((t) => t.type === 'sell')

    const totalSpent = buyTrades.reduce((sum, t) => sum + t.total_price, 0)
    const totalEarned = sellTrades.reduce((sum, t) => sum + t.total_price, 0)
    const totalVolume = tradeList.reduce((sum, t) => sum + t.quantity, 0)

    const avgBuyPrice =
      buyTrades.length > 0
        ? buyTrades.reduce((sum, t) => sum + t.price_per_credit, 0) / buyTrades.length
        : 0

    const avgSellPrice =
      sellTrades.length > 0
        ? sellTrades.reduce((sum, t) => sum + t.price_per_credit, 0) / sellTrades.length
        : 0

    return {
      total_trades: tradeList.length,
      total_volume: totalVolume,
      total_spent: totalSpent,
      total_earned: totalEarned,
      net_position: totalEarned - totalSpent,
      avg_buy_price: avgBuyPrice,
      avg_sell_price: avgSellPrice,
      completed_count: completedTrades.length,
      pending_count: tradeList.filter((t) => t.status === 'pending').length,
      cancelled_count: tradeList.filter((t) => t.status === 'cancelled').length,
    }
  }, [])

  /**
   * Fetch trading volume
   */
  const fetchTradingVolume = useCallback(async (days = 30) => {
    try {
      const response = await api.get<any>(`/marketplace/analytics/volume?days=${days}`)

      // Transform response to TradingVolume array
      const volumeData: TradingVolume[] = response.volume_data || []
      setMonthlyVolume(volumeData)
    } catch (err: any) {
      console.error('Error fetching trading volume:', err)
    }
  }, [])

  return {
    // State
    trades,
    metrics,
    isExecuting,
    error,

    // Actions
    executeTrade,
    fetchTradeHistory,
    completeTrade,

    // Analytics
    calculateMetrics,
    monthlyVolume,
    fetchTradingVolume,
  }
}
