import { Plus, Trash2, RotateCw, Wallet, Zap, Target, ArrowRight } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Dialog, Input, Textarea, Spinner } from '../components/ui'
import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts'

interface CreditBatch {
  id: string
  name: string
  totalCredits: number
  creditsRemaining: number
  createdAt: string
  quality: number
  value: number
  status: 'active' | 'retired' | 'traded'
  vintageYear: number
}

interface RetirementRecord {
  id: string
  quantity: number
  date: string
  reason: string
}

const mockBatches: CreditBatch[] = [
  {
    id: '1',
    name: 'Energy Efficiency Improvements Q1 2026',
    totalCredits: 500,
    creditsRemaining: 450,
    createdAt: '2026-01-15',
    quality: 95,
    value: 16912.50,
    status: 'active',
    vintageYear: 2025,
  },
  {
    id: '2',
    name: 'Renewable Energy Integration',
    totalCredits: 300,
    creditsRemaining: 125,
    createdAt: '2025-12-10',
    quality: 88,
    value: 5250,
    status: 'traded',
    vintageYear: 2025,
  },
  {
    id: '3',
    name: 'Cooling System Optimization',
    totalCredits: 200,
    creditsRemaining: 0,
    createdAt: '2025-11-20',
    quality: 92,
    value: 0,
    status: 'retired',
    vintageYear: 2025,
  },
]

const mockRetirements: RetirementRecord[] = [
  {
    id: '1',
    quantity: 50,
    date: '2026-03-05',
    reason: 'Compliance requirement for 2025 emissions reporting',
  },
  {
    id: '2',
    quantity: 125,
    date: '2026-02-20',
    reason: 'Voluntary offset for corporate sustainability commitment',
  },
]

const mockValueHistory = [
  { month: 'Jan', value: 24000 },
  { month: 'Feb', value: 26500 },
  { month: 'Mar', value: 22162.50 },
]

export function Portfolio() {
  const [batches, setBatches] = useState<CreditBatch[]>(mockBatches)
  const [retirements, setRetirements] = useState<RetirementRecord[]>(mockRetirements)
  const [isCreateBatchOpen, setIsCreateBatchOpen] = useState(false)
  const [isRetireCreditsOpen, setIsRetireCreditsOpen] = useState(false)
  const [selectedBatch, setSelectedBatch] = useState<CreditBatch | null>(null)
  const [formData, setFormData] = useState({
    batchName: '',
    quantity: '',
    description: '',
  })
  const [retireData, setRetireData] = useState({
    quantity: '',
    reason: '',
  })
  const [isLoading, setIsLoading] = useState(false)

  const totalCredits = batches.reduce((sum, b) => sum + b.creditsRemaining, 0)
  const totalValue = batches.reduce((sum, b) => sum + b.value, 0)
  const activeCount = batches.filter(b => b.status === 'active').length

  const handleCreateBatch = async () => {
    if (!formData.batchName || !formData.quantity) return

    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))

      const newBatch: CreditBatch = {
        id: `batch_${Date.now()}`,
        name: formData.batchName,
        totalCredits: parseFloat(formData.quantity),
        creditsRemaining: parseFloat(formData.quantity),
        createdAt: new Date().toISOString().split('T')[0],
        quality: 100,
        value: parseFloat(formData.quantity) * 35.5,
        status: 'active',
        vintageYear: new Date().getFullYear() - 1,
      }

      setBatches([...batches, newBatch])
      setFormData({ batchName: '', quantity: '', description: '' })
      setIsCreateBatchOpen(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRetireCredits = async () => {
    if (!selectedBatch || !retireData.quantity || !retireData.reason) return

    setIsLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))

      const quantity = parseFloat(retireData.quantity)
      const newRetirement: RetirementRecord = {
        id: `ret_${Date.now()}`,
        quantity,
        date: new Date().toISOString().split('T')[0],
        reason: retireData.reason,
      }

      setRetirements([...retirements, newRetirement])

      // Update batch
      const updatedBatches = batches.map(b =>
        b.id === selectedBatch.id
          ? {
              ...b,
              creditsRemaining: Math.max(0, b.creditsRemaining - quantity),
              value: Math.max(0, b.value - (quantity * b.value / b.totalCredits)),
              status: b.creditsRemaining - quantity === 0 ? 'retired' : b.status,
            }
          : b
      )
      setBatches(updatedBatches)

      setRetireData({ quantity: '', reason: '' })
      setSelectedBatch(null)
      setIsRetireCreditsOpen(false)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Carbon Credit Portfolio</h1>
        <p className="text-slate-400">Manage your carbon credits, batches, and retirement records</p>
      </section>

      {/* Portfolio Summary */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-green-600/20 to-green-700/20 border-green-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Credits</p>
                <p className="text-2xl font-bold text-white">{totalCredits.toLocaleString()}</p>
              </div>
              <Wallet className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-600/20 to-blue-700/20 border-blue-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Portfolio Value</p>
                <p className="text-2xl font-bold text-white">${totalValue.toFixed(0)}</p>
              </div>
              <Zap className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-cyan-600/20 to-cyan-700/20 border-cyan-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Active Batches</p>
                <p className="text-2xl font-bold text-white">{activeCount}</p>
              </div>
              <Target className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-600/20 to-purple-700/20 border-purple-500/30">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Retired</p>
                <p className="text-2xl font-bold text-white">
                  {retirements.reduce((sum, r) => sum + r.quantity, 0).toLocaleString()}
                </p>
              </div>
              <RotateCw className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Value Trend */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-white">Portfolio Value Trend</CardTitle>
            <CardDescription>Historical value of your carbon credits</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={mockValueHistory}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="month" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                  labelStyle={{ color: '#e2e8f0' }}
                  formatter={(value) => `$${value}`}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#3b82f6"
                  fillOpacity={1}
                  fill="url(#colorValue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-white">Quick Actions</CardTitle>
            <CardDescription>Manage your portfolio</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={() => setIsCreateBatchOpen(true)}
              className="w-full gap-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              <Plus className="w-4 h-4" />
              Create New Batch
            </Button>
            <Button
              variant="outline"
              onClick={() => setIsRetireCreditsOpen(true)}
              disabled={totalCredits === 0}
              className="w-full gap-2"
            >
              <RotateCw className="w-4 h-4" />
              Retire Credits
            </Button>
            <Button
              variant="outline"
              className="w-full gap-2"
            >
              <ArrowRight className="w-4 h-4" />
              List for Sale
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Credit Batches */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Credit Batches</CardTitle>
            <CardDescription>Manage your carbon credit batches</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {batches.map((batch) => (
                <div
                  key={batch.id}
                  className="border border-slate-700 rounded-lg p-4 hover:bg-slate-800/50 transition"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="font-semibold text-white">{batch.name}</h3>
                        <Badge
                          className={
                            batch.status === 'active'
                              ? 'bg-green-600/20 text-green-300 border-green-500/30'
                              : batch.status === 'retired'
                              ? 'bg-gray-600/20 text-gray-300 border-gray-500/30'
                              : 'bg-blue-600/20 text-blue-300 border-blue-500/30'
                          }
                        >
                          {batch.status.charAt(0).toUpperCase() + batch.status.slice(1)}
                        </Badge>
                      </div>
                      <p className="text-sm text-slate-400">
                        Vintage Year: {batch.vintageYear} • Created: {batch.createdAt}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-white">${batch.value.toFixed(2)}</p>
                      <p className="text-sm text-slate-400">Quality: {batch.quality}%</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Total Credits</p>
                      <p className="text-lg font-semibold text-white">{batch.totalCredits.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Remaining</p>
                      <p className="text-lg font-semibold text-blue-400">{batch.creditsRemaining.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Used</p>
                      <p className="text-lg font-semibold text-orange-400">
                        {(batch.totalCredits - batch.creditsRemaining).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="w-full bg-slate-700 rounded-full h-2 mb-4">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${(batch.creditsRemaining / batch.totalCredits) * 100}%` }}
                    />
                  </div>

                  <div className="flex gap-2">
                    {batch.status === 'active' && batch.creditsRemaining > 0 && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedBatch(batch)
                            setIsRetireCreditsOpen(true)
                          }}
                          className="gap-2"
                        >
                          <RotateCw className="w-4 h-4" />
                          Retire
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="gap-2"
                        >
                          <ArrowRight className="w-4 h-4" />
                          List for Sale
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Retirement History */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle className="text-white">Retirement History</CardTitle>
            <CardDescription>Record of retired carbon credits</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Date</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Quantity</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {retirements.map((record) => (
                    <tr key={record.id} className="border-b border-slate-700/50">
                      <td className="py-4 px-4 text-slate-300">{record.date}</td>
                      <td className="py-4 px-4 text-right font-semibold text-white">
                        {record.quantity.toLocaleString()}
                      </td>
                      <td className="py-4 px-4 text-slate-400">{record.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Create Batch Dialog */}
      <Dialog open={isCreateBatchOpen} onOpenChange={setIsCreateBatchOpen}>
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-white">Create New Batch</CardTitle>
              <CardDescription>Register a new carbon credit batch</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm text-slate-300">Batch Name</label>
                <Input
                  placeholder="e.g., Energy Efficiency Q1 2026"
                  value={formData.batchName}
                  onChange={(e) => setFormData({ ...formData, batchName: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-slate-300">Quantity (Credits)</label>
                <Input
                  type="number"
                  placeholder="500"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm text-slate-300">Description (Optional)</label>
                <Textarea
                  placeholder="Additional details about this batch..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setIsCreateBatchOpen(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateBatch}
                  disabled={!formData.batchName || !formData.quantity || isLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isLoading ? 'Creating...' : 'Create Batch'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </Dialog>

      {/* Retire Credits Dialog */}
      <Dialog open={isRetireCreditsOpen} onOpenChange={setIsRetireCreditsOpen}>
        {selectedBatch && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle className="text-white">Retire Credits</CardTitle>
                <CardDescription>Retire carbon credits from {selectedBatch.name}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                  <p className="text-sm text-slate-400 mb-1">Available Credits</p>
                  <p className="text-2xl font-bold text-white">{selectedBatch.creditsRemaining.toLocaleString()}</p>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-slate-300">Quantity to Retire</label>
                  <Input
                    type="number"
                    placeholder="Enter quantity"
                    value={retireData.quantity}
                    onChange={(e) => setRetireData({ ...retireData, quantity: e.target.value })}
                    max={selectedBatch.creditsRemaining}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-slate-300">Retirement Reason</label>
                  <Textarea
                    placeholder="Why are you retiring these credits?"
                    value={retireData.reason}
                    onChange={(e) => setRetireData({ ...retireData, reason: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setIsRetireCreditsOpen(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleRetireCredits}
                    disabled={!retireData.quantity || !retireData.reason || isLoading}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                  >
                    {isLoading ? 'Processing...' : 'Retire Credits'}
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
