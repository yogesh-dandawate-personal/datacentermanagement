/**
 * ListingForm Component
 * Create or edit marketplace listings
 */

import { useState, useEffect } from 'react'
import { Upload, X, Check, AlertCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input, Textarea, Select, Badge, Alert, Spinner } from '../ui'
import type { CreateListingRequest, ListingType, CreditBatch } from '../../types/marketplace'
import { useMarketplace } from '../../hooks/useMarketplace'
import { usePortfolio } from '../../hooks/usePortfolio'

interface ListingFormProps {
  onSuccess?: () => void
  onCancel?: () => void
  initialData?: Partial<CreateListingRequest>
}

export function ListingForm({ onSuccess, onCancel, initialData }: ListingFormProps) {
  const { createListing } = useMarketplace()
  const { batches, fetchBatches } = usePortfolio()

  const [formData, setFormData] = useState<Partial<CreateListingRequest>>({
    batch_id: initialData?.batch_id || '',
    quantity: initialData?.quantity || 0,
    price_per_credit: initialData?.price_per_credit || 0,
    listing_type: initialData?.listing_type || 'fixed_price',
    expires_in_days: initialData?.expires_in_days || 30,
    minimum_bid: initialData?.minimum_bid,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [imagePreview, setImagePreview] = useState<string | null>(null)

  // Auto-save to localStorage
  useEffect(() => {
    const interval = setInterval(() => {
      if (formData.batch_id || formData.quantity || formData.price_per_credit) {
        localStorage.setItem('listing_form_draft', JSON.stringify(formData))
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [formData])

  // Load draft on mount
  useEffect(() => {
    const draft = localStorage.getItem('listing_form_draft')
    if (draft && !initialData) {
      try {
        const parsedDraft = JSON.parse(draft)
        setFormData(parsedDraft)
      } catch (err) {
        console.error('Failed to load draft:', err)
      }
    }

    // Fetch available batches
    fetchBatches()
  }, [fetchBatches, initialData])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.batch_id) {
      newErrors.batch_id = 'Please select a credit batch'
    }

    if (!formData.quantity || formData.quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0'
    }

    if (!formData.price_per_credit || formData.price_per_credit <= 0) {
      newErrors.price_per_credit = 'Price must be greater than 0'
    }

    if (formData.listing_type === 'auction' && (!formData.minimum_bid || formData.minimum_bid <= 0)) {
      newErrors.minimum_bid = 'Minimum bid is required for auctions'
    }

    if (!formData.expires_in_days || formData.expires_in_days <= 0) {
      newErrors.expires_in_days = 'Expiry days must be greater than 0'
    }

    // Check if selected batch has enough credits
    if (formData.batch_id && formData.quantity) {
      const selectedBatch = batches.find((b) => b.id === formData.batch_id)
      if (selectedBatch && formData.quantity > selectedBatch.credits_remaining) {
        newErrors.quantity = `Only ${selectedBatch.credits_remaining} credits available in this batch`
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      await createListing(formData as CreateListingRequest)

      // Clear form and localStorage
      setFormData({
        batch_id: '',
        quantity: 0,
        price_per_credit: 0,
        listing_type: 'fixed_price',
        expires_in_days: 30,
        minimum_bid: undefined,
      })
      localStorage.removeItem('listing_form_draft')

      // Show success
      setShowSuccess(true)
      setTimeout(() => {
        setShowSuccess(false)
        if (onSuccess) onSuccess()
      }, 2000)
    } catch (err: any) {
      setErrors({ submit: err.message || 'Failed to create listing' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const clearDraft = () => {
    localStorage.removeItem('listing_form_draft')
    setFormData({
      batch_id: '',
      quantity: 0,
      price_per_credit: 0,
      listing_type: 'fixed_price',
      expires_in_days: 30,
      minimum_bid: undefined,
    })
  }

  const selectedBatch = batches.find((b) => b.id === formData.batch_id)
  const estimatedTotal = (formData.quantity || 0) * (formData.price_per_credit || 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-white">Create Marketplace Listing</CardTitle>
        <CardDescription>List your carbon credits for sale on the marketplace</CardDescription>
      </CardHeader>
      <CardContent>
        {showSuccess && (
          <Alert variant="success" className="mb-6">
            <Check className="w-4 h-4" />
            <span>Listing created successfully!</span>
          </Alert>
        )}

        {errors.submit && (
          <Alert variant="error" className="mb-6">
            <AlertCircle className="w-4 h-4" />
            <span>{errors.submit}</span>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Batch Selection */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">
              Select Credit Batch <span className="text-red-400">*</span>
            </label>
            <Select
              value={formData.batch_id}
              onChange={(e) => setFormData({ ...formData, batch_id: e.target.value })}
              className={errors.batch_id ? 'border-red-500' : ''}
            >
              <option value="">Choose a batch...</option>
              {batches
                .filter((b) => b.status === 'active' && b.credits_remaining > 0)
                .map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {batch.batch_name} ({batch.credits_remaining.toLocaleString()} credits available)
                  </option>
                ))}
            </Select>
            {errors.batch_id && <p className="text-xs text-red-400">{errors.batch_id}</p>}
            {selectedBatch && (
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Available</p>
                    <p className="text-white font-semibold">{selectedBatch.credits_remaining.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Quality</p>
                    <p className="text-white font-semibold">{selectedBatch.quality_score}%</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Vintage</p>
                    <p className="text-white font-semibold">{selectedBatch.vintage_year}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Listing Type */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">
              Listing Type <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              {(['fixed_price', 'auction', 'negotiable'] as ListingType[]).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFormData({ ...formData, listing_type: type })}
                  className={`p-3 rounded-lg border transition ${
                    formData.listing_type === type
                      ? 'border-blue-500 bg-blue-600/20 text-blue-300'
                      : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <div className="text-sm font-medium capitalize">{type.replace('_', ' ')}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Quantity and Price */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                max={selectedBatch?.credits_remaining}
                className={errors.quantity ? 'border-red-500' : ''}
              />
              {errors.quantity && <p className="text-xs text-red-400">{errors.quantity}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm text-slate-300 font-medium">
                Price per Credit ($) <span className="text-red-400">*</span>
              </label>
              <Input
                type="number"
                placeholder="35.50"
                step="0.01"
                value={formData.price_per_credit || ''}
                onChange={(e) => setFormData({ ...formData, price_per_credit: parseFloat(e.target.value) || 0 })}
                min="0.01"
                className={errors.price_per_credit ? 'border-red-500' : ''}
              />
              {errors.price_per_credit && <p className="text-xs text-red-400">{errors.price_per_credit}</p>}
            </div>
          </div>

          {/* Minimum Bid (for auctions) */}
          {formData.listing_type === 'auction' && (
            <div className="space-y-2">
              <label className="text-sm text-slate-300 font-medium">
                Minimum Bid ($) <span className="text-red-400">*</span>
              </label>
              <Input
                type="number"
                placeholder="30.00"
                step="0.01"
                value={formData.minimum_bid || ''}
                onChange={(e) => setFormData({ ...formData, minimum_bid: parseFloat(e.target.value) || 0 })}
                min="0.01"
                className={errors.minimum_bid ? 'border-red-500' : ''}
              />
              {errors.minimum_bid && <p className="text-xs text-red-400">{errors.minimum_bid}</p>}
            </div>
          )}

          {/* Expiry */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">
              Listing Expiry (days) <span className="text-red-400">*</span>
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[7, 14, 30, 60].map((days) => (
                <button
                  key={days}
                  type="button"
                  onClick={() => setFormData({ ...formData, expires_in_days: days })}
                  className={`p-2 rounded-lg border text-sm transition ${
                    formData.expires_in_days === days
                      ? 'border-blue-500 bg-blue-600/20 text-blue-300'
                      : 'border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  {days} days
                </button>
              ))}
            </div>
            <Input
              type="number"
              placeholder="Custom days"
              value={formData.expires_in_days || ''}
              onChange={(e) => setFormData({ ...formData, expires_in_days: parseInt(e.target.value) || 0 })}
              min="1"
              className={`mt-2 ${errors.expires_in_days ? 'border-red-500' : ''}`}
            />
            {errors.expires_in_days && <p className="text-xs text-red-400">{errors.expires_in_days}</p>}
          </div>

          {/* Image Upload (Optional) */}
          <div className="space-y-2">
            <label className="text-sm text-slate-300 font-medium">Batch Image (Optional)</label>
            <div className="border-2 border-dashed border-slate-700 rounded-lg p-6">
              {imagePreview ? (
                <div className="relative">
                  <img src={imagePreview} alt="Preview" className="w-full h-32 object-cover rounded-lg" />
                  <button
                    type="button"
                    onClick={() => setImagePreview(null)}
                    className="absolute top-2 right-2 p-1 bg-red-600 rounded-full hover:bg-red-700"
                  >
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              ) : (
                <label className="flex flex-col items-center gap-2 cursor-pointer">
                  <Upload className="w-8 h-8 text-slate-400" />
                  <span className="text-sm text-slate-400">Click to upload image</span>
                  <input type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                </label>
              )}
            </div>
          </div>

          {/* Summary */}
          {formData.quantity && formData.price_per_credit && (
            <div className="bg-blue-600/10 rounded-lg p-4 border border-blue-500/30 space-y-2">
              <h4 className="font-semibold text-white mb-2">Listing Summary</h4>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Total Credits:</span>
                <span className="text-white font-semibold">{formData.quantity.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Price per Credit:</span>
                <span className="text-white font-semibold">${formData.price_per_credit.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Platform Fee (1%):</span>
                <span className="text-white font-semibold">${(estimatedTotal * 0.01).toFixed(2)}</span>
              </div>
              <div className="border-t border-blue-500/30 pt-2 flex justify-between">
                <span className="text-slate-200 font-semibold">You will receive:</span>
                <span className="text-blue-400 font-bold text-lg">${(estimatedTotal * 0.99).toFixed(2)}</span>
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
              type="button"
              variant="outline"
              onClick={clearDraft}
              className="flex-1"
            >
              Clear Draft
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isSubmitting ? (
                <>
                  <Spinner size="sm" />
                  Creating...
                </>
              ) : (
                'Create Listing'
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
