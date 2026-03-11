/**
 * TradeForm Component
 * Execute buy/sell trades for carbon credits
 */

import { useState, useEffect } from 'react'
import { DollarSign, TrendingUp, AlertCircle, Check } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input, Select, Badge, Alert, Spinner } from '../ui'
import type { ExecuteTradeRequest, MarketplaceListing } from '../../types/marketplace'
import { useMarketplace } from '../../hooks/useMarketplace'
import { useTrading } from '../../hooks/useTrading'

interface TradeFormProps {
  preselectedListingId?: string
  onSuccess?: () => void
  onCancel?: () => void
}

export function TradeForm({ preselectedListingId, onSuccess, onCancel }: TradeFormProps) {
  const { listings, fetchListings } = useMarketplace()
  const { executeTrade, isExecuting, error: tradeError } = useTrading()

  const [formData, setFormData] = useState<Partial<ExecuteTradeRequest>>({
    listing_id: preselectedListingId || '',
    quantity: 0,
    agreed_price: undefined,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [showSuccess, setShowSuccess] = useState(false)
  const [paymentMethod, setPaymentMethod] = useState<'credit_card' | 'bank_transfer' | 'crypto'>('credit_card')

  useEffect(() => {
    fetchListings()
  }, [fetchListings])

  useEffect(() => {
    if (preselectedListingId) {
      setFormData((prev) => ({ ...prev, listing_id: preselectedListingId }))
    }
  }, [preselectedListingId])

  const selectedListing = listings.find((l) => l.id === formData.listing_id)

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.listing_id) {
      newErrors.listing_id = 'Please select a listing'
    }

    if (!formData.quantity || formData.quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0'
    }

    if (selectedListing && formData.quantity && formData.quantity > selectedListing.quantity_available) {
      newErrors.quantity = `Only ${selectedListing.quantity_available} credits available`
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      await executeTrade(formData as ExecuteTradeRequest)

      // Reset form
      setFormData({
        listing_id: '',
        quantity: 0,
        agreed_price: undefined,
      })

      // Show success
      setShowSuccess(true)
      setTimeout(() => {
        setShowSuccess(false)
        if (onSuccess) onSuccess()
      }, 2000)
    } catch (err: any) {
      setErrors({ submit: err.message || 'Failed to execute trade' })
    }
  }

  const subtotal = selectedListing && formData.quantity
    ? formData.quantity * (formData.agreed_price || selectedListing.price_per_credit)
    : 0
  const tradingFee = subtotal * 0.02
  const totalCost = subtotal + tradingFee

  // Market comparison (mock)
  const marketAvgPrice = 36.25
  const priceDifference = selectedListing
    ? ((selectedListing.price_per_credit - marketAvgPrice) / marketAvgPrice) * 100
    : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-white">Execute Trade</CardTitle>
        <CardDescription>Purchase carbon credits from the marketplace</CardDescription>
      </CardHeader>
      <CardContent>
        {showSuccess && (
          <Alert variant="success" className="mb-6">
            <Check className="w-4 h-4" />
            <span>Trade executed successfully!</span>
          </Alert>
        )}

        {(errors.submit || tradeError) && (
          <Alert variant="error" className="mb-6">
            <AlertCircle className="w-4 h-4" />
            <span>{errors.submit || tradeError}</span>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Listing Selection */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">
              Select Listing <span className="text-red-400">*</span>
            </label>
            <Select
              value={formData.listing_id}
              onChange={(e) => {
                const listing = listings.find((l) => l.id === e.target.value)
                setFormData({
                  ...formData,
                  listing_id: e.target.value,
                  agreed_price: listing?.price_per_credit,
                })
              }}
              className={errors.listing_id ? 'border-red-500' : ''}
              disabled={!!preselectedListingId}
            >
              <option value="">Choose a listing...</option>
              {listings
                .filter((l) => l.status === 'active')
                .map((listing) => (
                  <option key={listing.id} value={listing.id}>
                    {listing.batch_name} - ${listing.price_per_credit.toFixed(2)}/credit ({listing.quantity_available.toLocaleString()} available)
                  </option>
                ))}
            </Select>
            {errors.listing_id && <p className="text-xs text-red-400">{errors.listing_id}</p>}
          </div>

          {/* Listing Details */}
          {selectedListing && (
            <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold text-white">{selectedListing.batch_name}</h4>
                  <p className="text-sm text-slate-400">Seller: {selectedListing.seller_name}</p>
                </div>
                <Badge className="bg-green-600/20 text-green-300 border-green-500/30">
                  Quality {selectedListing.quality_score}%
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-slate-400">Price/Credit</p>
                  <p className="text-lg font-bold text-white">${selectedListing.price_per_credit.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Available</p>
                  <p className="text-lg font-bold text-white">{selectedListing.quantity_available.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">vs Market</p>
                  <p className={`text-lg font-bold ${priceDifference > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {priceDifference > 0 ? '+' : ''}{priceDifference.toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Market Comparison Alert */}
              {priceDifference < -5 && (
                <Alert variant="success">
                  <TrendingUp className="w-4 h-4" />
                  <span>Great deal! {Math.abs(priceDifference).toFixed(1)}% below market average</span>
                </Alert>
              )}
              {priceDifference > 5 && (
                <Alert variant="warning">
                  <AlertCircle className="w-4 h-4" />
                  <span>Price is {priceDifference.toFixed(1)}% above market average</span>
                </Alert>
              )}
            </div>
          )}

          {/* Quantity */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">
              Quantity <span className="text-red-400">*</span>
            </label>
            <Input
              type="number"
              placeholder="Enter quantity"
              value={formData.quantity || ''}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 0 })}
              min="1"
              max={selectedListing?.quantity_available}
              className={errors.quantity ? 'border-red-500' : ''}
            />
            {errors.quantity && <p className="text-xs text-red-400">{errors.quantity}</p>}
            {selectedListing && (
              <p className="text-xs text-slate-400">
                Max: {selectedListing.quantity_available.toLocaleString()} credits
              </p>
            )}
          </div>

          {/* Agreed Price (for negotiable listings) */}
          {selectedListing?.listing_type === 'negotiable' && (
            <div className="space-y-2">
              <label className="text-sm text-slate-300 font-medium">
                Offer Price per Credit ($)
              </label>
              <Input
                type="number"
                placeholder={selectedListing.price_per_credit.toFixed(2)}
                step="0.01"
                value={formData.agreed_price || ''}
                onChange={(e) => setFormData({ ...formData, agreed_price: parseFloat(e.target.value) || undefined })}
                min="0.01"
              />
              <p className="text-xs text-slate-400">
                Listed price: ${selectedListing.price_per_credit.toFixed(2)}
              </p>
            </div>
          )}

          {/* Payment Method */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">Payment Method</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'credit_card', label: 'Credit Card' },
                { value: 'bank_transfer', label: 'Bank Transfer' },
                { value: 'crypto', label: 'Crypto' },
              ].map((method) => (
                <button
                  key={method.value}
                  type="button"
                  onClick={() => setPaymentMethod(method.value as any)}
                  className={`p-3 rounded-lg border transition ${
                    paymentMethod === method.value
                      ? 'border-blue-500 bg-blue-600/20 text-blue-300'
                      : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="text-sm font-medium">{method.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Order Summary */}
          {formData.quantity && formData.quantity > 0 && selectedListing && (
            <div className="bg-blue-600/10 rounded-lg p-4 border border-blue-500/30 space-y-2">
              <h4 className="font-semibold text-white mb-2 flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Order Summary
              </h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">
                    {formData.quantity.toLocaleString()} credits × $
                    {(formData.agreed_price || selectedListing.price_per_credit).toFixed(2)}
                  </span>
                  <span className="text-white font-semibold">${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-300">Trading Fee (2%)</span>
                  <span className="text-white font-semibold">${tradingFee.toFixed(2)}</span>
                </div>
                <div className="border-t border-blue-500/30 pt-2 flex justify-between">
                  <span className="text-slate-200 font-semibold">Total Cost</span>
                  <span className="text-blue-400 font-bold text-xl">${totalCost.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            {onCancel && (
              <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              disabled={isExecuting || !formData.listing_id || !formData.quantity}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isExecuting ? (
                <>
                  <Spinner size="sm" />
                  Processing...
                </>
              ) : (
                'Execute Trade'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
