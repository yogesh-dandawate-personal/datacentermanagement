import { ArrowUpRight, ArrowDownRight, Zap, Leaf, TrendingUp, Activity } from 'lucide-react'

export function Dashboard() {
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Monitor your datacenter's environmental impact in real-time</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon
          const isPositive = stat.trend === 'up'
          return (
            <div
              key={i}
              className="group p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl hover:border-blue-500/50 transition"
            >
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
            </div>
          )
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
        {/* Energy Consumption Chart */}
        <div className="lg:col-span-2 p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl">
          <h3 className="text-lg font-bold text-white mb-6">Energy Consumption Trend</h3>
          <div className="h-64 bg-slate-900/30 rounded-lg flex items-center justify-center border border-slate-700/30">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-slate-600 mx-auto mb-2" />
              <p className="text-slate-500">Loading chart...</p>
            </div>
          </div>
        </div>

        {/* Top Facilities */}
        <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl">
          <h3 className="text-lg font-bold text-white mb-6">Top Facilities</h3>
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
        </div>
      </div>

      {/* Recent Activity */}
      <div className="p-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl">
        <h3 className="text-lg font-bold text-white mb-6">Recent Activity</h3>
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
      </div>
    </div>
  )
}
