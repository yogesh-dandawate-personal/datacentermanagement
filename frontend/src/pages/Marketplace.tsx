import { Search, Filter, ShoppingCart, TrendingUp, BarChart3, DollarSign } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Input, Badge, Dialog } from '../components/ui'
import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface CarbonListing {
  id: string
  batchName: string
  quantity: number
  pricePerCredit: number
  totalValue: number
  listingType: 'fixed_price' | 'auction' | 'negotiable'
  seller: string
  expiresAt: string
  quality: number
}

interface MarketAnalytics {
  currentPrice: number
  trend: number[]
  volume: number
  trades: number
}

const mockListings: CarbonListing[] = [
  {
    id: '1',
    batchName: 'Data Center Efficiency Credits Q1 2026',
    quantity: 500,
    pricePerCredit: 35.50,
    totalValue: 17750,
    listingType: 'fixed_price',
    seller: 'GreenTech Industries',
    expiresAt: '2026-04-10',
    quality: 95,
  },
  {
    id: '2',
    batchName: 'Renewable Energy Integration Batch',
    quantity: 250,
    pricePerCredit: 42.00,
    totalValue: 10500,
    listingType: 'auction',
    seller: 'Carbon Neutral Corp',
    expiresAt: '2026-03-25',
    quality: 88,
  },
  {
    id: '3',
    batchName: 'Energy Optimization Credits 2025',
    quantity: 1000,
    pricePerCredit: 28.75,
    totalValue: 28750,
    listingType: 'negotiable',
    seller: 'Sustainable Solutions Inc',
    expiresAt: '2026-05-15',
    quality: 92,
  },
  {
    id: '4',
    batchName: 'Verified Carbon Offsets',
    quantity: 750,
    pricePerCredit: 39.99,
    totalValue: 29992.50,
    listingType: 'fixed_price',
    seller: 'EcoBalance Ltd',
    expiresAt: '2026-04-20',
    quality: 98,
  },
]

const mockPriceHistory = [
  { date: 'Mar 4', price: 32.5 },
  { date: 'Mar 5', price: 33.2 },
  { date: 'Mar 6', price: 34.1 },
  { date: 'Mar 7', price: 35.8 },
  { date: 'Mar 8', price: 36.2 },
  { date: 'Mar 9', price: 37.5 },
  { date: 'Mar 10', price: 38.1 },
]

const mockVolumeData = [
  { date: 'Week 1', volume: 1200, trades: 24 },
  { date: 'Week 2', volume: 1850, trades: 32 },
  { date: 'Week 3', volume: 1450, trades: 28 },
  { date: 'Week 4', volume: 2100, trades: 41 },
]

export function Marketplace() {
  const [listings, setListings] = useState<CarbonListing[]>(mockListings)
  const [filteredListings, setFilteredListings] = useState<CarbonListing[]>(mockListings)
  const [searchTerm, setSearchTerm] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')
  const [selectedListing, setSelectedListing] = useState<CarbonListing | null>(null)
  const [tradeQuantity, setTradeQuantity] = useState('')
  const [isTradeDialogOpen, setIsTradeDialogOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    let filtered = listings

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(l =>
        l.batchName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        l.seller.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by price range
    if (minPrice) {
      filtered = filtered.filter(l => l.pricePerCredit >= parseFloat(minPrice))
    }
    if (maxPrice) {
      filtered = filtered.filter(l => l.pricePerCredit <= parseFloat(maxPrice))
    }

    setFilteredListings(filtered)
  }, [listings, searchTerm, minPrice, maxPrice])

  const handleExecuteTrade = async () => {
    if (!selectedListing || !tradeQuantity) return

    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))

      // Mock success
      console.log('Trade executed:', {
        listing: selectedListing,
        quantity: tradeQuantity,
        totalPrice: parseFloat(tradeQuantity) * selectedListing.pricePerCredit
      })

      setIsTradeDialogOpen(false)
      setTradeQuantity('')
      setSelectedListing(null)
      // Show success toast would go here
    } finally {
      setIsLoading(false)
    }
  }

  const avgPrice = listings.length > 0
    ? (listings.reduce((sum, l) => sum + l.pricePerCredit, 0) / listings.length).toFixed(2)
    : '0'

  const totalAvailable = listings.reduce((sum, l) => sum + l.quantity, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Carbon Credit Marketplace</h1>
        <p className="text-slate-400">Discover and trade carbon credits to meet your sustainability goals</p>
      </section>

      {/* Market Overview */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-600/20 to-blue-700/20 border-blue-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Average Price</p>
                <p className="text-2xl font-bold text-white">${avgPrice}</p>
              </div>
              <DollarSign className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-600/20 to-green-700/20 border-green-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Available</p>
                <p className="text-2xl font-bold text-white">{totalAvailable.toLocaleString()}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-cyan-600/20 to-cyan-700/20 border-cyan-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Market Listings</p>
                <p className="text-2xl font-bold text-white">{listings.length}</p>
              </div>
              <ShoppingCart className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-600/20 to-purple-700/20 border-purple-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Market Status</p>
                <p className="text-2xl font-bold text-white">Active</p>
              </div>
              <BarChart3 className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Charts */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Price Trend (7 Days)</CardTitle>
            <CardDescription>Average carbon credit price movement</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={mockPriceHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3b82f6"
                  dot={{ fill: '#3b82f6' }}
                  name="Price (USD)"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-white">Trading Volume (Monthly)</CardTitle>
            <CardDescription>Credits traded and transaction count</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={mockVolumeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Bar dataKey="volume" fill="#10b981" name="Credits Traded" />
                <Bar dataKey="trades" fill="#06b6d4" name="Transactions" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </section>

      {/* Search & Filter */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Available Listings</CardTitle>
            <CardDescription>Browse and purchase carbon credits from verified sellers</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search and Filters */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                  <Input
                    type="text"
                    placeholder="Search by batch name or seller..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <Button variant="outline" className="gap-2">
                  <Filter className="w-4 h-4" />
                  Advanced Filters
                </Button>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <Input
                  type="number"
                  placeholder="Min Price"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white"
                />
                <Input
                  type="number"
                  placeholder="Max Price"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>

            {/* Listings Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Batch Name</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Quantity</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Price/Credit</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Total Value</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Quality</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Type</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredListings.length > 0 ? (
                    filteredListings.map((listing) => (
                      <tr key={listing.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition">
                        <td className="py-4 px-4">
                          <div>
                            <p className="text-white font-medium">{listing.batchName}</p>
                            <p className="text-xs text-slate-400">by {listing.seller}</p>
                          </div>
                        </td>
                        <td className="text-right py-4 px-4 text-white">{listing.quantity.toLocaleString()}</td>
                        <td className="text-right py-4 px-4 text-white font-semibold">${listing.pricePerCredit.toFixed(2)}</td>
                        <td className="text-right py-4 px-4 text-white">${listing.totalValue.toLocaleString('en-US', { maximumFractionDigits: 2 })}</td>
                        <td className="text-center py-4 px-4">
                          <Badge className="bg-blue-600/20 text-blue-300 border-blue-500/30">
                            {listing.quality}%
                          </Badge>
                        </td>
                        <td className="text-center py-4 px-4">
                          <Badge
                            className={
                              listing.listingType === 'fixed_price'
                                ? 'bg-green-600/20 text-green-300 border-green-500/30'
                                : listing.listingType === 'auction'
                                ? 'bg-yellow-600/20 text-yellow-300 border-yellow-500/30'
                                : 'bg-purple-600/20 text-purple-300 border-purple-500/30'
                            }
                          >
                            {listing.listingType.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="text-center py-4 px-4">
                          <Button
                            size="sm"
                            onClick={() => {
                              setSelectedListing(listing)
                              setIsTradeDialogOpen(true)
                            }}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                          >
                            Buy
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-400">
                        No listings match your criteria
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Trade Dialog */}
      <Dialog open={isTradeDialogOpen} onOpenChange={setIsTradeDialogOpen}>
        {selectedListing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-white">Execute Trade</CardTitle>
                <CardDescription>Purchase carbon credits from {selectedListing.seller}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg p-4 space-y-3 border border-slate-700">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Batch:</span>
                    <span className="text-white font-medium">{selectedListing.batchName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Available:</span>
                    <span className="text-white font-medium">{selectedListing.quantity.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Price/Unit:</span>
                    <span className="text-white font-medium">${selectedListing.pricePerCredit.toFixed(2)}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-slate-300">Quantity to Purchase</label>
                  <Input
                    type="number"
                    placeholder="Enter quantity"
                    value={tradeQuantity}
                    onChange={(e) => setTradeQuantity(e.target.value)}
                    max={selectedListing.quantity}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                {tradeQuantity && (
                  <div className="bg-blue-600/10 rounded-lg p-4 border border-blue-500/30 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Subtotal:</span>
                      <span className="text-white font-semibold">
                        ${(parseFloat(tradeQuantity) * selectedListing.pricePerCredit).toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Trading Fee (2%):</span>
                      <span className="text-white font-semibold">
                        ${(parseFloat(tradeQuantity) * selectedListing.pricePerCredit * 0.02).toFixed(2)}
                      </span>
                    </div>
                    <div className="border-t border-blue-500/30 pt-2 flex justify-between">
                      <span className="text-slate-200 font-semibold">Total:</span>
                      <span className="text-blue-400 font-bold text-lg">
                        ${(parseFloat(tradeQuantity) * selectedListing.pricePerCredit * 1.02).toFixed(2)}
                      </span>
                    </div>
                  </div>
                )}

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setIsTradeDialogOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleExecuteTrade}
                    disabled={!tradeQuantity || isLoading}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {isLoading ? 'Processing...' : 'Execute Trade'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </Dialog>
    </div>
  )
}
