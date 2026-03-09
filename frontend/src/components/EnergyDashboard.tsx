import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function EnergyDashboard() {
  const energyData = [
    { hour: '00:00', usage: 450, renewable: 180 },
    { hour: '04:00', usage: 380, renewable: 150 },
    { hour: '08:00', usage: 520, renewable: 280 },
    { hour: '12:00', usage: 680, renewable: 420 },
    { hour: '16:00', usage: 750, renewable: 350 },
    { hour: '20:00', usage: 620, renewable: 240 },
    { hour: '24:00', usage: 480, renewable: 200 },
  ]

  const carbonData = [
    { month: 'Jan', emissions: 4500, target: 4200 },
    { month: 'Feb', emissions: 4300, target: 4200 },
    { month: 'Mar', emissions: 4100, target: 4200 },
    { month: 'Apr', emissions: 3900, target: 4200 },
    { month: 'May', emissions: 3800, target: 4200 },
    { month: 'Jun', emissions: 3700, target: 4200 },
  ]

  return (
    <div className="space-y-8">
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Energy Usage (24h)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={energyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="hour" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
            <Legend />
            <Line type="monotone" dataKey="usage" stroke="#3b82f6" strokeWidth={2} dot={false} name="Total Usage (kW)" />
            <Line type="monotone" dataKey="renewable" stroke="#10b981" strokeWidth={2} dot={false} name="Renewable (kW)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-6">Carbon Emissions Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={carbonData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
            <Legend />
            <Bar dataKey="emissions" fill="#ef4444" name="Actual (kg CO₂)" />
            <Bar dataKey="target" fill="#10b981" name="Target (kg CO₂)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
