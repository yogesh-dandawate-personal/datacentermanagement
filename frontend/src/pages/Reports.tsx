import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Table, Pagination, Select, Spinner, Alert } from '../components/ui'
import { FileText, Download, Eye, Trash2, Filter, Search } from 'lucide-react'
import { useState } from 'react'
import { useReports, useComplianceMetrics } from '../hooks/useApi'

const complianceData = [
  { month: 'Jan', scope1: 450, scope2: 380, scope3: 520 },
  { month: 'Feb', scope1: 430, scope2: 360, scope3: 500 },
  { month: 'Mar', scope1: 410, scope2: 340, scope3: 480 },
  { month: 'Apr', scope1: 390, scope2: 320, scope3: 460 },
  { month: 'May', scope1: 370, scope2: 300, scope3: 440 },
  { month: 'Jun', scope1: 350, scope2: 280, scope3: 420 },
]

const allReports = [
  {
    id: 1,
    name: 'Q2 2026 ESG Report',
    date: 'June 15, 2026',
    status: 'Complete',
    size: '2.4 MB',
    compliance: 'ISO 14001',
    type: 'ESG'
  },
  {
    id: 2,
    name: 'Q1 2026 ESG Report',
    date: 'March 15, 2026',
    status: 'Complete',
    size: '2.3 MB',
    compliance: 'ISO 14001',
    type: 'ESG'
  },
  {
    id: 3,
    name: 'Carbon Reduction Plan',
    date: 'March 10, 2026',
    status: 'Pending Review',
    size: '1.8 MB',
    compliance: 'GHG Protocol',
    type: 'Compliance'
  },
  {
    id: 4,
    name: 'Sustainability Goals Update',
    date: 'March 5, 2026',
    status: 'Complete',
    size: '3.2 MB',
    compliance: 'SASB',
    type: 'Strategic'
  },
  {
    id: 5,
    name: 'Monthly Energy Audit',
    date: 'February 28, 2026',
    status: 'Complete',
    size: '1.5 MB',
    compliance: 'ISO 50001',
    type: 'Audit'
  },
  {
    id: 6,
    name: 'Scope 3 Emissions Analysis',
    date: 'February 20, 2026',
    status: 'Complete',
    size: '2.1 MB',
    compliance: 'GHG Protocol',
    type: 'Analysis'
  },
]

const auditTrail = [
  { id: 1, action: 'Report Q2 2026 generated', user: 'admin@company.com', time: '2 hours ago', type: 'generated' },
  { id: 2, action: 'Emissions data verified', user: 'auditor@company.com', time: '4 hours ago', type: 'verified' },
  { id: 3, action: 'Report approved for publication', user: 'manager@company.com', time: '1 day ago', type: 'approved' },
  { id: 4, action: 'Data import completed', user: 'system', time: '2 days ago', type: 'imported' },
  { id: 5, action: 'Baseline established', user: 'analyst@company.com', time: '1 week ago', type: 'created' },
]

export function Reports() {
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  // Fetch data from API
  const reportsData = useReports(searchTerm, filterType !== 'all' ? filterType : undefined, filterStatus !== 'all' ? filterStatus : undefined, currentPage, 5)
  const complianceData = useComplianceMetrics()

  const itemsPerPage = 5

  // Use API data or fallback
  const reports = reportsData.data?.reports || allReports
  const totalPages = reportsData.data?.pages || Math.ceil(allReports.length / itemsPerPage)
  const paginatedReports = reports.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const isLoading = reportsData.loading || complianceData.loading
  const hasError = reportsData.error || complianceData.error
  const hasReports = paginatedReports.length > 0

  const handleGenerateReport = () => {
    // TODO: Open report generation dialog
    console.log('Generate new report')
  }

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {hasError && (
        <Alert
          variant="error"
          title="Data Loading Error"
          message={hasError?.message || 'Failed to load reports. Using fallback data.'}
          action={
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                reportsData.refetch()
                complianceData.refetch()
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
          <h1 className="text-3xl font-bold text-white mb-2">Reports & Compliance</h1>
          <p className="text-slate-400">Generate and manage ESG compliance reports</p>
        </div>
        <Button
          variant="primary"
          size="lg"
          className="flex items-center gap-2"
          onClick={handleGenerateReport}
        >
          <FileText className="w-5 h-5" />
          New Report
        </Button>
      </div>

      {/* Compliance Metrics */}
      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <Spinner size="lg" message="Loading compliance metrics..." />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-slate-400 text-sm">Total Emissions (6M)</p>
              <p className="text-3xl font-bold text-white mt-2">
                {complianceData.data?.total_emissions.toLocaleString() || '2,350'} tCO₂e
              </p>
              <p className="text-sm text-success-400 mt-1">↓ 12% vs previous period</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <p className="text-slate-400 text-sm">Compliance Rate</p>
              <p className="text-3xl font-bold text-white mt-2">
                {complianceData.data?.compliance_rate.toFixed(1) || '94.5'}%
              </p>
              <p className="text-sm text-success-400 mt-1">↑ 2.3% from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <p className="text-slate-400 text-sm">Reports Generated</p>
              <p className="text-3xl font-bold text-white mt-2">
                {complianceData.data?.reports_generated || '24'}
              </p>
              <p className="text-sm text-slate-400 mt-1">This fiscal year</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Emissions Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Scope 1, 2, 3 Emissions Trend</CardTitle>
          <CardDescription>Monthly breakdown of carbon emissions by scope</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="w-full h-96 animate-pulse bg-slate-800/50 rounded flex items-end justify-around p-8 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="flex-1 bg-slate-700/50 rounded-t" style={{ height: `${Math.random() * 100 + 20}%` }} />
              ))}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={complianceData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" style={{ fontSize: '12px' }} />
                <YAxis stroke="#64748b" style={{ fontSize: '12px' }} label={{ value: 'tCO₂e', angle: -90, position: 'insideLeft' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #64748b',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#f1f5f9' }}
                  formatter={(value) => `${value} tCO₂e`}
                />
                <Legend wrapperStyle={{ paddingTop: '20px', color: '#cbd5e1' }} />
                <Bar dataKey="scope1" stackId="a" fill="#ef4444" name="Scope 1" />
                <Bar dataKey="scope2" stackId="a" fill="#f59e0b" name="Scope 2" />
                <Bar dataKey="scope3" stackId="a" fill="#0ea5e9" name="Scope 3" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Reports List with Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Reports & Documents</CardTitle>
          <CardDescription>Access and manage your compliance documents</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setCurrentPage(1)
                }}
                className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:border-primary-500/50 focus:outline-none transition"
              />
            </div>

            <Select
              options={[
                { value: 'all', label: 'All Types' },
                { value: 'ESG', label: 'ESG Reports' },
                { value: 'Compliance', label: 'Compliance' },
                { value: 'Audit', label: 'Audits' },
                { value: 'Strategic', label: 'Strategic' },
                { value: 'Analysis', label: 'Analysis' },
              ]}
              value={filterType}
              onChange={(e) => {
                setFilterType(e.target.value)
                setCurrentPage(1)
              }}
            />

            <Select
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'Complete', label: 'Complete' },
                { value: 'Pending Review', label: 'Pending Review' },
              ]}
              value={filterStatus}
              onChange={(e) => {
                setFilterStatus(e.target.value)
                setCurrentPage(1)
              }}
            />
          </div>

          {/* Reports Table */}
          {!hasReports ? (
            <div className="py-12 text-center">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium text-white mb-2">No reports yet</h3>
              <p className="text-slate-400 mb-6">Generate your first compliance report to get started</p>
              <Button variant="primary" onClick={handleGenerateReport}>
                <FileText className="w-4 h-4 mr-2" />
                Generate First Report
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-800/50 border-b border-slate-700/30">
                    <th className="px-6 py-4 text-left font-semibold text-slate-200">Name</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-200">Date</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-200">Type</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-200">Status</th>
                    <th className="px-6 py-4 text-left font-semibold text-slate-200">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedReports.map((report) => (
                    <tr key={report.id} className="border-b border-slate-700/30 hover:bg-slate-800/30 transition">
                      <td className="px-6 py-4 text-slate-300">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-primary-400" />
                          <div>
                            <p className="font-medium text-white">{report.name}</p>
                            <p className="text-xs text-slate-400">{report.size}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-slate-300">{report.date}</td>
                      <td className="px-6 py-4">
                        <Badge variant="info" size="sm">{report.type}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        <Badge
                          variant={report.status === 'Complete' ? 'success' : 'warning'}
                          size="sm"
                        >
                          {report.status}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" className="flex items-center gap-1" title="View">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="flex items-center gap-1" title="Download">
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {hasReports && totalPages > 1 && (
            <div className="flex justify-center mt-6">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Audit Trail */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Trail</CardTitle>
          <CardDescription>Track all changes and compliance events</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {auditTrail.map((entry) => (
              <div key={entry.id} className="py-3 border-b border-slate-700/30 last:border-0 flex items-start gap-3">
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                  entry.type === 'generated' ? 'bg-primary-400' :
                  entry.type === 'verified' ? 'bg-success-400' :
                  entry.type === 'approved' ? 'bg-success-500' :
                  'bg-slate-400'
                }`}></div>
                <div className="flex-1 min-w-0">
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
