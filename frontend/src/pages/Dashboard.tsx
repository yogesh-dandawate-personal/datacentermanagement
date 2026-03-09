import { ArrowUpRight, ArrowDownRight, Zap, Leaf, TrendingUp, Activity } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, SkeletonStat, SkeletonChart, SkeletonTable, ErrorBoundary } from '../components/ui'
import { useState, useEffect } from 'react'

const energyTrendData = [
  { hour: '00:00', usage: 450, target: 400 },
  { hour: '04:00', usage: 380, target: 400 },
  { hour: '08:00', usage: 520, target: 400 },
  { hour: '12:00', usage: 680, target: 400 },
  { hour: '16:00', usage: 750, target: 400 },
  { hour: '20:00', usage: 620, target: 400 },
  { hour: '24:00', usage: 480, target: 400 },
]

export function Dashboard() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => setIsLoading(false), 2000)
    return () => clearTimeout(timer)
  }, [])

  const stats = [
    {
      title: 'Total Energy Usage',
      value: '2,456.34',
      unit: 'kWh',
      change: '+12.5%',
      trend: 'up',
      icon: Zap,
      color: 'from-blue-500 to-blue-600',
    },
    {
      title: 'Carbon Emissions',
      value: '1,234.56',
      unit: 'kg CO₂',
      change: '-8.2%',
      trend: 'down',
      icon: Leaf,
      color: 'from-green-500 to-green-600',
    },
    {
      title: 'Energy Efficiency',
      value: '87.5',
      unit: '%',
      change: '+5.3%',
      trend: 'up',
      icon: TrendingUp,
      color: 'from-cyan-500 to-cyan-600',
    },
    {
      title: 'Active Facilities',
      value: '12',
      unit: 'facilities',
      change: '+2',
      trend: 'up',
      icon: Activity,
      color: 'from-purple-500 to-purple-600',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Monitor your datacenter's environmental impact in real-time</p>
      </section>

      {/* Stats Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" aria-label="Key performance indicators">
        {isLoading ? (
          <>
            <SkeletonStat />
            <SkeletonStat />
            <SkeletonStat />
            <SkeletonStat />
          </>
        ) : (
          stats.map((stat, i) => {
            const Icon = stat.icon
            const isPositive = stat.trend === 'up'
            return (
              <Card key={i} className="group hover:border-primary-500/50">
                <CardContent>
                {/* Header with Icon */}
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-slate-300 text-sm font-medium">{stat.title}</h3>
                  <div
                    className={`p-3 bg-gradient-to-br ${stat.color} rounded-lg opacity-80 group-hover:opacity-100 transition`}
                  >
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                </div>

                {/* Main Value */}
                <div className="mb-4">
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold text-white">{stat.value}</span>
                    <span className="text-sm text-slate-400">{stat.unit}</span>
                  </div>
                </div>

                {/* Change Indicator */}
                <div
                  className={`flex items-center gap-1 text-sm font-medium ${
                    isPositive && stat.change.includes('+') && stat.title.includes('Carbon')
                      ? 'text-green-400'
                      : isPositive && !stat.change.includes('-')
                        ? 'text-green-400'
                        : 'text-red-400'
                  }`}
                >
                  {isPositive ? (
                    <ArrowUpRight className="w-4 h-4" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4" />
                  )}
                  {stat.change} from last month
                </div>
                </CardContent>
              </Card>
            )
          })
        )}
      </div>

      {/* Charts Section */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8" aria-label="Energy analytics">
        {/* Energy Consumption Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Energy Consumption Trend (24h)</CardTitle>
            <CardDescription>Real-time energy usage vs target</CardDescription>
          </CardHeader>
          <CardContent>
            <ErrorBoundary>
              {isLoading ? (
                <SkeletonChart height={300} />
              ) : (
                <div className="w-full h-80">
                  <ResponsiveContainer width="100%" height={320}>
                    <LineChart data={energyTrendData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="hour" stroke="#64748b" style={{ fontSize: '12px' }} />
                      <YAxis
                        stroke="#64748b"
                        style={{ fontSize: '12px' }}
                        label={{ value: 'Power (kW)', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          border: '1px solid #64748b',
                          borderRadius: '8px',
                          padding: '8px 12px',
                        }}
                        labelStyle={{ color: '#f1f5f9' }}
                        formatter={(value) => `${value} kW`}
                      />
                      <Legend
                        wrapperStyle={{ paddingTop: '20px', color: '#cbd5e1' }}
                        iconType="line"
                      />
                      <Line
                        type="monotone"
                        dataKey="usage"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                        name="Actual Usage (kW)"
                      />
                      <Line
                        type="monotone"
                        dataKey="target"
                        stroke="#ef4444"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={false}
                        name="Target (kW)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </ErrorBoundary>
          </CardContent>
        </Card>

        {/* Top Facilities */}
        <Card>
          <CardHeader>
            <CardTitle>Top Facilities</CardTitle>
            <CardDescription>Current energy usage</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <SkeletonTable rows={3} cols={2} />
            ) : (
              <div className="space-y-3">
                {[
                  { name: 'DC East 1', usage: '456 kWh', percentage: 85 },
                  { name: 'DC West 1', usage: '345 kWh', percentage: 72 },
                  { name: 'DC Central', usage: '234 kWh', percentage: 58 },
                ].map((facility, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-white">{facility.name}</span>
                      <span className="text-xs text-slate-400">{facility.usage}</span>
                    </div>
                    <div className="w-full h-2 bg-slate-900/50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                        style={{ width: `${facility.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest events and alerts</CardDescription>
          </CardHeader>
        <CardContent>
          {isLoading ? (
            <SkeletonTable rows={3} cols={3} />
          ) : (
            <div className="space-y-4">
              {[
                {
                  action: 'Carbon emissions exceeded target',
                  facility: 'DC East 1',
                  time: '2 hours ago',
                  severity: 'warning',
                },
                {
                  action: 'Energy efficiency improved',
                  facility: 'DC Central',
                  time: '5 hours ago',
                  severity: 'success',
                },
                {
                  action: 'Monthly report generated',
                  facility: 'All Facilities',
                  time: '1 day ago',
                  severity: 'info',
                },
              ].map((activity, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-slate-900/30 rounded-lg border border-slate-700/30">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      activity.severity === 'warning'
                        ? 'bg-yellow-500'
                        : activity.severity === 'success'
                          ? 'bg-green-500'
                          : 'bg-blue-500'
                    }`}
                  ></div>
                  <div className="flex-1">
                    <p className="text-white text-sm font-medium">{activity.action}</p>
                    <p className="text-slate-400 text-xs">{activity.facility}</p>
                  </div>
                  <span className="text-slate-500 text-xs">{activity.time}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      </section>
    </div>
  )
}
