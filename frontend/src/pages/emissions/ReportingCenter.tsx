/**
 * Emissions Reporting Center
 * Generate and manage ESG compliance reports (GHG Protocol, CDP, GRI, TCFD)
 */

import { useState } from 'react'
import { Card, Button, Badge, Dialog, Alert } from '@/components/ui'
import { FileText, Download, Eye, Plus, AlertCircle } from 'lucide-react'

const reportTypes = [
  {
    id: 'ghg_protocol',
    name: 'GHG Protocol Report',
    description: 'Corporate Accounting & Reporting Standard with Scope 1, 2, 3',
    status: 'available',
  },
  {
    id: 'cdp',
    name: 'CDP Climate Change Report',
    description: 'Environmental Disclosure Platform questionnaire',
    status: 'available',
  },
  {
    id: 'gri',
    name: 'GRI Standards Report',
    description: 'Global Reporting Initiative sustainability report',
    status: 'available',
  },
  {
    id: 'tcfd',
    name: 'TCFD Report',
    description: 'Climate-related Financial Disclosures framework',
    status: 'available',
  },
  {
    id: 'sec_climate',
    name: 'SEC Climate Report',
    description: 'SEC climate risk and emissions disclosure',
    status: 'coming_soon',
  },
]

const recentReports = [
  {
    id: '1',
    type: 'GHG Protocol Report',
    year: 2025,
    status: 'published',
    createdAt: '2026-02-15',
    size: '2.4 MB',
  },
  {
    id: '2',
    type: 'TCFD Report',
    year: 2025,
    status: 'approved',
    createdAt: '2026-02-10',
    size: '1.8 MB',
  },
  {
    id: '3',
    type: 'GRI Standards Report',
    year: 2025,
    status: 'pending_review',
    createdAt: '2026-02-08',
    size: '3.1 MB',
  },
]

export default function ReportingCenter() {
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [showGenerateDialog, setShowGenerateDialog] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)

  const handleGenerateReport = async (reportType: string) => {
    setGeneratingReport(true)
    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setGeneratingReport(false)
    setShowGenerateDialog(false)
  }

  const statusConfig = {
    published: { color: 'text-green-400', bg: 'bg-green-500/20', badge: 'success' },
    approved: { color: 'text-blue-400', bg: 'bg-blue-500/20', badge: 'info' },
    pending_review: { color: 'text-orange-400', bg: 'bg-orange-500/20', badge: 'warning' },
    draft: { color: 'text-slate-400', bg: 'bg-slate-500/20', badge: 'outline' },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Reporting Center</h1>
          <p className="text-slate-400 mt-1">Generate and manage ESG compliance reports</p>
        </div>

        <Button variant="primary" onClick={() => setShowGenerateDialog(true)}>
          <Plus className="w-4 h-4" />
          Generate Report
        </Button>
      </div>

      {/* Available Report Types */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Report Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reportTypes.map((report) => (
            <Card
              key={report.id}
              className={`cursor-pointer transition ${
                report.status === 'coming_soon' ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-500/50'
              }`}
              onClick={() => {
                if (report.status !== 'coming_soon') {
                  setSelectedReport(report.id)
                  setShowGenerateDialog(true)
                }
              }}
            >
              <div className="flex items-start justify-between mb-3">
                <FileText className="w-6 h-6 text-blue-400" />
                {report.status === 'coming_soon' && (
                  <Badge variant="outline" className="text-xs">
                    Coming Soon
                  </Badge>
                )}
              </div>

              <h3 className="font-semibold mb-2">{report.name}</h3>
              <p className="text-sm text-slate-400 mb-4">{report.description}</p>

              <Button
                variant="outline"
                size="sm"
                className="w-full"
                disabled={report.status === 'coming_soon'}
              >
                {report.status === 'coming_soon' ? 'Coming Soon' : 'Generate'}
              </Button>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Reports */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Reports</h2>

        {recentReports.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Report Type</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Year</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Created</th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">Actions</th>
                </tr>
              </thead>

              <tbody>
                {recentReports.map((report) => {
                  const statusConfig_ = statusConfig[report.status as keyof typeof statusConfig]

                  return (
                    <tr key={report.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition">
                      <td className="py-3 px-4">{report.type}</td>
                      <td className="py-3 px-4">{report.year}</td>
                      <td className="py-3 px-4">
                        <Badge variant={statusConfig_?.badge as any} className="text-xs">
                          {report.status}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-400">
                        {new Date(report.createdAt).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button size="sm" variant="outline">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <Card>
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No reports generated yet</p>
              <p className="text-sm text-slate-500 mt-1">Generate your first ESG report</p>
            </div>
          </Card>
        )}
      </div>

      {/* Report Information Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold mb-3">GHG Protocol</h3>
          <p className="text-sm text-slate-400 mb-4">
            Corporate Accounting & Reporting Standard covering Scope 1, 2, and 3 emissions with detailed calculation
            methodology.
          </p>
          <a href="#" className="text-blue-400 hover:text-blue-300 text-sm">
            Learn more →
          </a>
        </Card>

        <Card>
          <h3 className="font-semibold mb-3">CDP Climate Change</h3>
          <p className="text-sm text-slate-400 mb-4">
            Environmental Disclosure Platform (CDP) questionnaire for transparent climate change reporting and
            governance.
          </p>
          <a href="#" className="text-blue-400 hover:text-blue-300 text-sm">
            Learn more →
          </a>
        </Card>
      </div>

      {/* Generate Report Dialog */}
      {showGenerateDialog && (
        <Dialog
          open={showGenerateDialog}
          onOpenChange={setShowGenerateDialog}
          title="Generate Report"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Report Type</label>
              <select
                value={selectedReport || ''}
                onChange={(e) => setSelectedReport(e.target.value)}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              >
                <option value="">Select a report type...</option>
                {reportTypes
                  .filter((r) => r.status !== 'coming_soon')
                  .map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Reporting Year</label>
              <input
                type="number"
                defaultValue={2025}
                className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Report Format</label>
              <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:border-blue-500 focus:outline-none">
                <option value="pdf">PDF</option>
                <option value="xlsx">Excel (XLSX)</option>
                <option value="json">JSON</option>
              </select>
            </div>

            <Alert variant="info">
              <AlertCircle className="w-5 h-5" />
              Report generation typically takes 1-2 minutes. You'll receive an email when it's ready.
            </Alert>

            <div className="flex gap-3 pt-4">
              <Button
                variant="primary"
                className="flex-1"
                onClick={() => handleGenerateReport(selectedReport || '')}
                disabled={!selectedReport || generatingReport}
              >
                {generatingReport ? 'Generating...' : 'Generate Report'}
              </Button>
              <Button variant="outline" onClick={() => setShowGenerateDialog(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </Dialog>
      )}
    </div>
  )
}
