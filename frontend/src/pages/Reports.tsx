import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { FileText, Download, Eye } from 'lucide-react'

const complianceData = [
  { month: 'Jan', scope1: 450, scope2: 380, scope3: 520 },
  { month: 'Feb', scope1: 430, scope2: 360, scope3: 500 },
  { month: 'Mar', scope1: 410, scope2: 340, scope3: 480 },
  { month: 'Apr', scope1: 390, scope2: 320, scope3: 460 },
  { month: 'May', scope1: 370, scope2: 300, scope3: 440 },
  { month: 'Jun', scope1: 350, scope2: 280, scope3: 420 },
]

const reportsList = [
  {
    name: 'Q1 2026 ESG Report',
    date: 'March 15, 2026',
    status: 'Complete',
    size: '2.4 MB',
    compliance: 'ISO 14001',
  },
  {
    name: 'Carbon Reduction Plan',
    date: 'March 10, 2026',
    status: 'Pending Review',
    size: '1.8 MB',
    compliance: 'GHG Protocol',
  },
  {
    name: 'Sustainability Goals Update',
    date: 'March 5, 2026',
    status: 'Complete',
    size: '3.2 MB',
    compliance: 'SASB',
  },
  {
    name: 'Monthly Energy Audit',
    date: 'February 28, 2026',
    status: 'Complete',
    size: '1.5 MB',
    compliance: 'ISO 50001',
  },
]

export function Reports() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Reports & Compliance</h1>
          <p className="text-slate-400">Generate and manage ESG compliance reports</p>
        </div>
        <Button size="lg" className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          New Report
        </Button>
      </div>

      {/* Compliance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-slate-400 text-sm">Total Emissions (6M)</p>
            <p className="text-3xl font-bold text-white mt-2">2,350 tCO₂e</p>
            <p className="text-sm text-red-400 mt-1">↓ 12% vs previous period</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-slate-400 text-sm">Compliance Rate</p>
            <p className="text-3xl font-bold text-white mt-2">94.5%</p>
            <p className="text-sm text-green-400 mt-1">↑ 2.3% from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <p className="text-slate-400 text-sm">Reports Generated</p>
            <p className="text-3xl font-bold text-white mt-2">24</p>
            <p className="text-sm text-slate-400 mt-1">This fiscal year</p>
          </CardContent>
        </Card>
      </div>

      {/* Emissions Trend */}
      <Card>
        <CardHeader>
          <CardTitle>Scope 1, 2, 3 Emissions Trend</CardTitle>
          <CardDescription>Monthly breakdown of carbon emissions by scope</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={complianceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" />
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
              <Bar dataKey="scope1" stackId="a" fill="#ef4444" name="Scope 1" />
              <Bar dataKey="scope2" stackId="a" fill="#f59e0b" name="Scope 2" />
              <Bar dataKey="scope3" stackId="a" fill="#3b82f6" name="Scope 3" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Recent Reports */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
          <CardDescription>Access and download your compliance documents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {reportsList.map((report, i) => (
              <div
                key={i}
                className="p-4 border border-slate-700/30 rounded-lg hover:border-blue-500/50 transition flex items-center justify-between"
              >
                <div className="flex-1">
                  <h4 className="font-medium text-white flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    {report.name}
                  </h4>
                  <div className="flex items-center gap-4 mt-2 text-sm text-slate-400">
                    <span>{report.date}</span>
                    <span>•</span>
                    <span>{report.size}</span>
                    <span>•</span>
                    <span className="px-2 py-1 bg-slate-900/50 rounded text-xs text-slate-300">
                      {report.compliance}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      report.status === 'Complete'
                        ? 'bg-green-900/30 text-green-300'
                        : 'bg-yellow-900/30 text-yellow-300'
                    }`}
                  >
                    {report.status}
                  </span>
                  <Button variant="ghost" size="sm" className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    View
                  </Button>
                  <Button variant="ghost" size="sm" className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Audit Trail */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Trail</CardTitle>
          <CardDescription>Track all changes and compliance events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {[
              { action: 'Report Q1 2026 generated', user: 'admin@company.com', time: '2h ago' },
              { action: 'Emissions data verified', user: 'auditor@company.com', time: '4h ago' },
              { action: 'Report approved for publication', user: 'manager@company.com', time: '1d ago' },
              { action: 'Data import completed', user: 'system', time: '2d ago' },
            ].map((entry, i) => (
              <div key={i} className="py-3 border-b border-slate-700/30 last:border-0 flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2"></div>
                <div className="flex-1">
                  <p className="text-white text-sm font-medium">{entry.action}</p>
                  <p className="text-slate-400 text-xs mt-1">
                    {entry.user} • {entry.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
