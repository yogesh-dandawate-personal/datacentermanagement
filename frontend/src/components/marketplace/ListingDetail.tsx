/**
 * ListingDetail Component
 * Full marketplace listing detail page with all information
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ShoppingCart, Star, TrendingUp, Calendar, Package, AlertCircle, Heart, Flag } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Spinner, Alert } from '../ui'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import type { MarketplaceListing, MarketPriceHistory } from '../../types/marketplace'
import { useMarketplace } from '../../hooks/useMarketplace'
import { useTrading } from '../../hooks/useTrading'

interface ListingDetailProps {
  listingId?: string
}

export function ListingDetail({ listingId: propListingId }: ListingDetailProps) {
  const { id: paramListingId } = useParams<{ id: string }>()
  const listingId = propListingId || paramListingId
  const navigate = useNavigate()

  const { fetchListingById, selectedListing, isLoading, error, priceHistory } = useMarketplace()
  const { executeTrade, isExecuting } = useTrading()

  const [quantity, setQuantity] = useState('')
  const [isWatchlisted, setIsWatchlisted] = useState(false)

  useEffect(() => {
    if (listingId) {
      fetchListingById(listingId)
    }
  }, [listingId, fetchListingById])

  if (isLoading || !selectedListing) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="error">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </Alert>
      </div>
    )
  }

  const listing = selectedListing

  const handleBuyNow = async () => {
    if (!quantity || parseInt(quantity) <= 0) {
      return
    }

    try {
      await executeTrade({
        listing_id: listing.id,
        quantity: parseInt(quantity),
        agreed_price: listing.price_per_credit,
      })

      // Show success and navigate
      navigate('/marketplace')
    } catch (err) {
      console.error('Trade execution failed:', err)
    }
  }

  const toggleWatchlist = () => {
    setIsWatchlisted(!isWatchlisted)
  }

  const reportListing = () => {
    // Report listing functionality
    alert('Report listing functionality coming soon')
  }

  // Mock price history for demonstration
  const mockPriceHistory: MarketPriceHistory[] = [
    { date: '2026-01-01', price: 32.5 },
    { date: '2026-01-15', price: 33.8 },
    { date: '2026-02-01', price: 34.2 },
    { date: '2026-02-15', price: 35.1 },
    { date: '2026-03-01', price: 34.8 },
    { date: '2026-03-11', price: listing.price_per_credit },
  ]

  // Mock seller rating
  const sellerRating = 4.7
  const sellerReviewCount = 142

  // Mock buyer reviews
  const buyerReviews = [
    {
      id: '1',
      buyerName: 'Green Energy Corp',
      rating: 5,
      date: '2026-03-05',
      comment: 'Excellent credits, fast processing, highly recommended!',
    },
    {
      id: '2',
      buyerName: 'Sustainable Solutions Inc',
      rating: 4,
      date: '2026-02-28',
      comment: 'Good quality credits, reasonable price.',
    },
    {
      id: '3',
      buyerName: 'EcoTech Industries',
      rating: 5,
      date: '2026-02-20',
      comment: 'Great transaction, seller was very responsive.',
    },
  ]

  // Calculate estimated total
  const estimatedTotal = quantity ? parseFloat(quantity) * listing.price_per_credit * 1.02 : 0

  return (
    <div className="space-y-6">
      {/* Back Navigation */}
      <div>
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="gap-2 text-slate-400 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Marketplace
        </Button>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header Card */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-2xl text-white mb-2">{listing.batch_name}</CardTitle>
                  <CardDescription>Listed by {listing.seller_name || 'Unknown Seller'}</CardDescription>
                </div>
                <Badge className="bg-green-600/20 text-green-300 border-green-500/30">
                  {listing.status === 'active' ? 'Available' : listing.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Key Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Price per Credit</p>
                  <p className="text-xl font-bold text-white">${listing.price_per_credit.toFixed(2)}</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Available</p>
                  <p className="text-xl font-bold text-white">{listing.quantity_available.toLocaleString()}</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Total Value</p>
                  <p className="text-xl font-bold text-white">${listing.total_value.toLocaleString()}</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Quality Score</p>
                  <p className="text-xl font-bold text-white">{listing.quality_score}%</p>
                </div>
              </div>

              {/* Listing Type & Expiry */}
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Package className="w-5 h-5 text-slate-400" />
                  <span className="text-slate-300">
                    Type: <span className="font-semibold text-white">{listing.listing_type.replace('_', ' ')}</span>
                  </span>
                </div>
                {listing.expires_at && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-slate-400" />
                    <span className="text-slate-300">
                      Expires: <span className="font-semibold text-white">{new Date(listing.expires_at).toLocaleDateString()}</span>
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Price History Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">Price History (6 Months)</CardTitle>
              <CardDescription>Historical price trend for similar credits</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mockPriceHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis
                    dataKey="date"
                    stroke="#94a3b8"
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short' })}
                  />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                    labelStyle={{ color: '#e2e8f0' }}
                    formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Seller Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">Seller Information</CardTitle>
              <CardDescription>Verified seller details and rating</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-white text-lg">{listing.seller_name}</h3>
                  <p className="text-sm text-slate-400">Member since 2024</p>
                </div>
                <div className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  <span className="text-xl font-bold text-white">{sellerRating}</span>
                  <span className="text-slate-400">({sellerReviewCount} reviews)</span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Total Sales</p>
                  <p className="text-lg font-bold text-white">2,450</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Response Time</p>
                  <p className="text-lg font-bold text-white">2h</p>
                </div>
                <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">Verification</p>
                  <p className="text-lg font-bold text-green-400">Verified</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Buyer Reviews */}
          <Card>
            <CardHeader>
              <CardTitle className="text-white">Buyer Reviews</CardTitle>
              <CardDescription>What other buyers are saying</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {buyerReviews.map((review) => (
                <div key={review.id} className="border-b border-slate-700 pb-4 last:border-b-0 last:pb-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-white">{review.buyerName}</h4>
                      <p className="text-xs text-slate-400">{new Date(review.date).toLocaleDateString()}</p>
                    </div>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: review.rating }).map((_, i) => (
                        <Star key={i} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      ))}
                    </div>
                  </div>
                  <p className="text-slate-300">{review.comment}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Purchase Actions */}
        <div className="lg:col-span-1">
          <div className="sticky top-6 space-y-4">
            {/* Purchase Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-white">Purchase Credits</CardTitle>
                <CardDescription>Complete your transaction</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm text-slate-300">Quantity</label>
                  <input
                    type="number"
                    placeholder="Enter quantity"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    max={listing.quantity_available}
                    min="1"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-slate-400">
                    Max: {listing.quantity_available.toLocaleString()} credits
                  </p>
                </div>

                {quantity && parseInt(quantity) > 0 && (
                  <div className="bg-blue-600/10 rounded-lg p-4 border border-blue-500/30 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">Subtotal:</span>
                      <span className="text-white font-semibold">
                        ${(parseInt(quantity) * listing.price_per_credit).toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-300">Trading Fee (2%):</span>
                      <span className="text-white font-semibold">
                        ${(parseInt(quantity) * listing.price_per_credit * 0.02).toFixed(2)}
                      </span>
                    </div>
                    <div className="border-t border-blue-500/30 pt-2 flex justify-between">
                      <span className="text-slate-200 font-semibold">Total:</span>
                      <span className="text-blue-400 font-bold text-lg">
                        ${estimatedTotal.toFixed(2)}
                      </span>
                    </div>
                  </div>
                )}

                <Button
                  onClick={handleBuyNow}
                  disabled={!quantity || parseInt(quantity) <= 0 || isExecuting}
                  className="w-full gap-2 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isExecuting ? (
                    <>
                      <Spinner size="sm" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <ShoppingCart className="w-4 h-4" />
                      Buy Now
                    </>
                  )}
                </Button>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={toggleWatchlist}
                    className="flex-1 gap-2"
                  >
                    <Heart className={`w-4 h-4 ${isWatchlisted ? 'fill-red-500 text-red-500' : ''}`} />
                    {isWatchlisted ? 'Watchlisted' : 'Add to Watchlist'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={reportListing}
                    className="gap-2"
                  >
                    <Flag className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Availability Calendar (Mock) */}
            <Card>
              <CardHeader>
                <CardTitle className="text-white text-sm">Availability</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Immediate</span>
                    <Badge className="bg-green-600/20 text-green-300 border-green-500/30">
                      Available
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Delivery</span>
                    <span className="text-sm text-white">1-2 business days</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Settlement</span>
                    <span className="text-sm text-white">T+2</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
