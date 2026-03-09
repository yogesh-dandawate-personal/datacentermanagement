import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Select, Input, Spinner, Alert } from '../components/ui'
import { Download, TrendingDown, Zap, Calendar, Filter } from 'lucide-react'
import { useState } from 'react'
import { useEnergyMetrics, useFacilities } from '../hooks/useApi'

// Fallback data for when API is not available
const fallbackEnergyTrendData = [
  { time: '00:00', usage: 450, renewable: 180, target: 400 },
  { time: '04:00', usage: 380, renewable: 150, target: 400 },
  { time: '08:00', usage: 520, renewable: 280, target: 400 },
  { time: '12:00', usage: 680, renewable: 420, target: 400 },
  { time: '16:00', usage: 750, renewable: 350, target: 400 },
  { time: '20:00', usage: 620, renewable: 240, target: 400 },
  { time: '24:00', usage: 480, renewable: 200, target: 400 },
]

const fallbackFacilities = [
  { id: 'dc-east-1', name: 'DC East 1', location: 'Virginia, USA', status: 'Active' as const },
  { id: 'dc-west-1', name: 'DC West 1', location: 'California, USA', status: 'Active' as const },
  { id: 'dc-central', name: 'DC Central', location: 'Texas, USA', status: 'Active' as const },
  { id: 'dc-eu-1', name: 'DC EU 1', location: 'Frankfurt, Germany', status: 'Active' as const },
]

export function Energy() {
  const [selectedFacility, setSelectedFacility] = useState('all')
  const [dateRange, setDateRange] = useState('24h')
  const [showFilters, setShowFilters] = useState(false)

  // Fetch data from API
  const energyMetrics = useEnergyMetrics(selectedFacility, dateRange)
  const facilitiesData = useFacilities()

  // Use real data or fallback
  const metrics = energyMetrics.data || {
    total_usage: 2456,
    renewable_percentage: 48.5,
    daily_cost: 4892,
    facilities: [],
    trend_data: fallbackEnergyTrendData,
  }

  const facilities = facilitiesData.data || fallbackFacilities

  // Transform data for pie chart
  const facilityBreakdown = facilities.map((f, i) => ({
    name: f.name,
    value: Math.floor(f.current_usage || (456 - i * 100)),
    fill: ['#0ea5e9', '#06b6d4', '#8b5cf6', '#a855f7'][i % 4],
  }))

  const facilityOptions = [
    { value: 'all', label: 'All Facilities' },
    ...allFacilities.map(f => ({ value: f.id, label: f.name }))
  ]

  const dateRangeOptions = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' },
    { value: '1y', label: 'Last Year' }
  ]

  // Handle loading state
  const isLoading = energyMetrics.loading || facilitiesData.loading
  const hasError = energyMetrics.error || facilitiesData.error

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {hasError && (
        <Alert
          variant="error"
          title="Data Loading Error"
          message={hasError?.message || 'Failed to load energy data. Using fallback data.'}
          action={
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                energyMetrics.refetch()
                facilitiesData.refetch()
              }}
            >
              Retry
            </Button>
          }
          onClose={() => {}}
        />
      )}

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Energy Management</h1>
          <p className="text-slate-400">Real-time energy consumption and optimization</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="md" className="flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </Button>
          <Button
            variant="ghost"
            size="md"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 md:hidden"
          >
            <Filter className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <Select
                label="Facility"
                options={[
                  { value: 'all', label: 'All Facilities' },
                  ...facilities.map(f => ({ value: f.id, label: f.name }))
                ]}
                value={selectedFacility}
                onChange={(e) => setSelectedFacility(e.target.value)}
              />
              <Select
                label="Time Range"
                options={dateRangeOptions}
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              />
              <div className="flex items-end gap-2">
                <Button variant="primary" className="flex-1" disabled={isLoading}>
                  {isLoading ? 'Loading...' : 'Apply Filters'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <Spinner size="lg" message="Loading energy metrics..." />
        </div>
      ) : (
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm">Current Usage</p>
                  <p className="text-3xl font-bold text-white mt-2">{metrics.total_usage.toLocaleString()} kW</p>
                  <p className="text-sm text-danger-400 mt-1 flex items-center gap-1">
                    <TrendingDown className="w-4 h-4" /> 12% above target
                  </p>
                </div>
                <Zap className="w-12 h-12 text-warning-400 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <p className="text-slate-400 text-sm">Renewable Energy</p>
              <p className="text-3xl font-bold text-white mt-2">{metrics.renewable_percentage}%</p>
              <div className="w-full h-2 bg-slate-900/50 rounded-full mt-3 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-success-500 to-success-400"
                  style={{ width: `${metrics.renewable_percentage}%` }}
                ></div>
              </div>
              <p className="text-xs text-slate-400 mt-2">↑ 5.2% from yesterday</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <p className="text-slate-400 text-sm">Daily Cost</p>
              <p className="text-3xl font-bold text-white mt-2">${metrics.daily_cost.toLocaleString()}</p>
              <p className="text-xs text-slate-400 mt-2">Estimated cost for today</p>
            </CardContent>
          </Card>
        </section>
      )}

      {/* Charts Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Energy Trend Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Energy Consumption Trend</CardTitle>
            <CardDescription>{dateRange === '24h' ? '24-hour' : dateRange} usage with renewable energy breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-[300px] flex items-center justify-center">
                <Spinner message="Loading chart..." />
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={metrics.trend_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Line type="monotone" dataKey="usage" stroke="#0ea5e9" strokeWidth={2} name="Usage (kW)" />
                <Line type="monotone" dataKey="renewable" stroke="#10b981" strokeWidth={2} name="Renewable (kW)" />
                <Line type="monotone" dataKey="target" stroke="#ef4444" strokeWidth={2} strokeDasharray="5 5" name="Target (kW)" />
              </LineChart>
            </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Facility Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Facility Breakdown</CardTitle>
            <CardDescription>Distribution by location</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={facilityBreakdown} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                  {facilityBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#e2e8f0' }}
                  formatter={(value) => `${value} kW`}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-3 mt-4">
              {facilityBreakdown.map((facility) => (
                <div key={facility.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: facility.fill }}></div>
                    <span className="text-slate-300">{facility.name}</span>
                  </div>
                  <span className="text-white font-medium">{facility.value} kW</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Facilities List */}
      <Card>
        <CardHeader>
          <CardTitle>Facilities</CardTitle>
          <CardDescription>All datacenter locations and their status</CardDescription>
        </CardHeader>
        <CardContent>
          {facilitiesData.loading ? (
            <div className="flex justify-center py-8">
              <Spinner message="Loading facilities..." />
            </div>
          ) : (
            <div className="space-y-3">
              {facilities.map((facility) => (
                <div key={facility.id} className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/30 hover:border-primary-500/30 transition flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{facility.name}</h4>
                    <p className="text-sm text-slate-400">{facility.location}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="success" size="sm">{facility.status}</Badge>
                    <Button variant="ghost" size="sm">View Details</Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Optimization Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Optimization Recommendations</CardTitle>
          <CardDescription>AI-powered insights to reduce energy consumption</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { title: 'Increase renewable usage', savings: '12-15%', priority: 'high', description: 'Shift load to peak solar hours' },
              { title: 'Optimize cooling cycles', savings: '8-10%', priority: 'medium', description: 'Implement variable frequency drives' },
              { title: 'Load balancing improvement', savings: '5-7%', priority: 'low', description: 'Redistribute workloads across facilities' },
            ].map((rec, i) => (
              <div key={i} className="p-4 border border-slate-700/30 rounded-lg hover:border-primary-500/50 transition">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h4 className="font-medium text-white">{rec.title}</h4>
                    <p className="text-xs text-slate-400 mt-1">{rec.description}</p>
                  </div>
                  <Badge
                    variant={
                      rec.priority === 'high'
                        ? 'danger'
                        : rec.priority === 'medium'
                          ? 'warning'
                          : 'info'
                    }
                    size="sm"
                  >
                    {rec.priority}
                  </Badge>
                </div>
                <p className="text-sm text-primary-400 font-semibold">Estimated savings: {rec.savings}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
