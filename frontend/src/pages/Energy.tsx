import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Download, TrendingDown, Zap } from 'lucide-react'

const energyTrendData = [
  { time: '00:00', usage: 450, renewable: 180, target: 400 },
  { time: '04:00', usage: 380, renewable: 150, target: 400 },
  { time: '08:00', usage: 520, renewable: 280, target: 400 },
  { time: '12:00', usage: 680, renewable: 420, target: 400 },
  { time: '16:00', usage: 750, renewable: 350, target: 400 },
  { time: '20:00', usage: 620, renewable: 240, target: 400 },
  { time: '24:00', usage: 480, renewable: 200, target: 400 },
]

const facilityBreakdown = [
  { name: 'DC East 1', value: 456, fill: '#3b82f6' },
  { name: 'DC West 1', value: 345, fill: '#06b6d4' },
  { name: 'DC Central', value: 234, fill: '#8b5cf6' },
]

export function Energy() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Energy Management</h1>
          <p className="text-slate-400">Real-time energy consumption and optimization</p>
        </div>
        <Button size="lg" className="flex items-center gap-2">
          <Download className="w-5 h-5" />
          Export Report
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Current Usage</p>
                <p className="text-3xl font-bold text-white mt-2">2,456 kW</p>
                <p className="text-sm text-red-400 mt-1 flex items-center gap-1">
                  <TrendingDown className="w-4 h-4" /> 12% above target
                </p>
              </div>
              <Zap className="w-12 h-12 text-yellow-400 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-slate-400 text-sm">Renewable Energy</p>
            <p className="text-3xl font-bold text-white mt-2">48.5%</p>
            <div className="w-full h-2 bg-slate-900/50 rounded-full mt-3 overflow-hidden">
              <div className="h-full w-[48.5%] bg-gradient-to-r from-green-500 to-emerald-500"></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-slate-400 text-sm">Daily Cost</p>
            <p className="text-3xl font-bold text-white mt-2">$4,892</p>
            <p className="text-sm text-slate-400 mt-1">Estimated daily cost</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Energy Trend */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Energy Consumption Trend</CardTitle>
            <CardDescription>24-hour usage with renewable energy breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={energyTrendData}>
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
                <Line type="monotone" dataKey="usage" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="renewable" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="target" stroke="#ef4444" strokeWidth={2} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
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
            <div className="space-y-2 mt-4">
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
      </div>

      {/* Optimization Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle>Optimization Recommendations</CardTitle>
          <CardDescription>AI-powered insights to reduce energy consumption</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { title: 'Increase renewable usage', savings: '12-15%', priority: 'High' },
              { title: 'Optimize cooling cycles', savings: '8-10%', priority: 'Medium' },
              { title: 'Load balancing improvement', savings: '5-7%', priority: 'Low' },
            ].map((rec, i) => (
              <div key={i} className="p-4 border border-slate-700/30 rounded-lg hover:border-blue-500/50 transition">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-white">{rec.title}</h4>
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      rec.priority === 'High'
                        ? 'bg-red-900/30 text-red-300'
                        : rec.priority === 'Medium'
                          ? 'bg-yellow-900/30 text-yellow-300'
                          : 'bg-blue-900/30 text-blue-300'
                    }`}
                  >
                    {rec.priority}
                  </span>
                </div>
                <p className="text-sm text-slate-400">Estimated savings: {rec.savings}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
