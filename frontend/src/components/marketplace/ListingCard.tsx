/**
 * ListingCard Component
 * Display carbon credit listing in card format
 */

import { Calendar, TrendingUp, Award, Building2 } from 'lucide-react'
import { Card, CardContent, Badge, Button } from '../ui'
import type { MarketplaceListing } from '../../types/marketplace'

export interface ListingCardProps {
  listing: MarketplaceListing
  onSelect?: (listing: MarketplaceListing) => void
  onBuy?: (listing: MarketplaceListing) => void
}

export function ListingCard({ listing, onSelect, onBuy }: ListingCardProps) {
  const getListingTypeColor = (type: string) => {
    switch (type) {
      case 'fixed_price':
        return 'bg-green-600/20 text-green-300 border-green-500/30'
      case 'auction':
        return 'bg-amber-600/20 text-amber-300 border-amber-500/30'
      case 'negotiable':
        return 'bg-purple-600/20 text-purple-300 border-purple-500/30'
      default:
        return 'bg-slate-600/20 text-slate-300 border-slate-500/30'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-600/20 text-green-300 border-green-500/30'
      case 'sold':
        return 'bg-blue-600/20 text-blue-300 border-blue-500/30'
      case 'expired':
        return 'bg-gray-600/20 text-gray-300 border-gray-500/30'
      case 'cancelled':
        return 'bg-red-600/20 text-red-300 border-red-500/30'
      default:
        return 'bg-slate-600/20 text-slate-300 border-slate-500/30'
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'No expiry'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const isExpiringSoon = () => {
    if (!listing.expires_at) return false
    const daysUntilExpiry = Math.ceil(
      (new Date(listing.expires_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
    )
    return daysUntilExpiry <= 7 && daysUntilExpiry > 0
  }

  return (
    <Card
      className="hover:border-primary-500/50 transition-all cursor-pointer group"
      onClick={() => onSelect?.(listing)}
    >
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-white text-lg mb-1 group-hover:text-primary-400 transition">
              {listing.batch_name || 'Unnamed Batch'}
            </h3>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Building2 className="w-4 h-4" />
              <span>{listing.seller_name || 'Unknown Seller'}</span>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <Badge className={getStatusColor(listing.status)}>
              {listing.status.charAt(0).toUpperCase() + listing.status.slice(1)}
            </Badge>
            <Badge className={getListingTypeColor(listing.listing_type)}>
              {listing.listing_type.replace('_', ' ')}
            </Badge>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
            <p className="text-xs text-slate-400 mb-1">Available Credits</p>
            <p className="text-xl font-bold text-white">{listing.quantity_available.toLocaleString()}</p>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50">
            <p className="text-xs text-slate-400 mb-1">Price per Credit</p>
            <p className="text-xl font-bold text-primary-400">${listing.price_per_credit.toFixed(2)}</p>
          </div>
        </div>

        {/* Quality Score */}
        {listing.quality_score && (
          <div className="flex items-center gap-2 mb-4">
            <Award className="w-4 h-4 text-amber-400" />
            <span className="text-sm text-slate-300">Quality Score:</span>
            <span className="text-sm font-semibold text-amber-400">{listing.quality_score}%</span>
          </div>
        )}

        {/* Expiry */}
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-400">
            {listing.expires_at ? (
              <>
                Expires: <span className={isExpiringSoon() ? 'text-amber-400 font-semibold' : ''}>
                  {formatDate(listing.expires_at)}
                </span>
                {isExpiringSoon() && <span className="text-amber-400 ml-2">(Soon!)</span>}
              </>
            ) : (
              'No expiration'
            )}
          </span>
        </div>

        {/* Total Value */}
        <div className="border-t border-slate-700/50 pt-4 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-400">Total Value</span>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-lg font-bold text-white">
                ${listing.total_value.toLocaleString('en-US', { maximumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        {listing.status === 'active' && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onSelect?.(listing)
              }}
              className="flex-1"
            >
              View Details
            </Button>
            <Button
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onBuy?.(listing)
              }}
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white"
            >
              Buy Now
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
