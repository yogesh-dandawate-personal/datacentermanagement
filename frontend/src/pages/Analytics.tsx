/**
 * Analytics Dashboard Page
 * Comprehensive analytics dashboard with emissions trends, forecasting, and sustainability scoring
 */

import { useState } from 'react'
import { Download, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react'
import { useAnalytics } from '../hooks/useAnalytics'
import { EmissionsTrendChart } from '../components/EmissionsTrendChart'
import { EnergyPatternAnalysis } from '../components/EnergyPatternAnalysis'
import { ForecastChart } from '../components/ForecastChart'
import { SustainabilityScore } from '../components/SustainabilityScore'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Select } from '../components/ui/Select'
import { Spinner } from '../components/ui/Spinner'
import { Alert } from '../components/ui/Alert'

export function Analytics() {
  const [timeRange, setTimeRange] = useState('12') // months
  const [exporting, setExporting] = useState(false)

  const {
    trends,
    patterns,
    forecast,
    sustainabilityScore,
    loading,
    error,
    refetch,
    exportAnalytics,
  } = useAnalytics(Number(timeRange), undefined, 30)

  const handleExport = async (format: 'pdf' | 'csv') => {
    setExporting(true)
    try {
      await exportAnalytics(format)
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setExporting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner size="lg" />
        <span className="ml-3 text-slate-400">Loading analytics...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert
          variant="error"
          title="Error Loading Analytics"
          message={error}
          action={
            <Button size="sm" variant="outline" onClick={() => refetch()}>
              Retry
            </Button>
          }
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-blue-400" />
            Analytics Dashboard
          </h1>
          <p className="text-slate-400 mt-1">
            Comprehensive emissions trends, forecasting, and sustainability insights
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            options={[
              { value: '3', label: '3 Months' },
              { value: '6', label: '6 Months' },
              { value: '12', label: '12 Months' },
              { value: '24', label: '24 Months' },
            ]}
          />

          <Button
            variant="outline"
            size="md"
            onClick={() => refetch()}
            icon={<RefreshCw className="w-4 h-4" />}
          >
            Refresh
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={() => handleExport('pdf')}
            loading={exporting}
            icon={<Download className="w-4 h-4" />}
          >
            Export PDF
          </Button>
        </div>
      </div>

      {/* Sustainability Score - Top Section */}
      {sustainabilityScore && (
        <SustainabilityScore score={sustainabilityScore} />
      )}

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Emissions Trend */}
        <Card className="lg:col-span-2">
          <div className="p-6 border-b border-slate-700/30">
            <h2 className="text-xl font-bold text-white">Emissions Trend Analysis</h2>
            <p className="text-sm text-slate-400 mt-1">
              12-month historical emissions with forecasting projection
            </p>
          </div>
          <div className="p-6">
            <EmissionsTrendChart trends={trends} />
          </div>
        </Card>

        {/* Energy Pattern Analysis */}
        <Card>
          <div className="p-6 border-b border-slate-700/30">
            <h2 className="text-xl font-bold text-white">Energy Pattern Analysis</h2>
            <p className="text-sm text-slate-400 mt-1">
              Peak detection and anomaly identification
            </p>
          </div>
          <div className="p-6">
            <EnergyPatternAnalysis patterns={patterns} />
          </div>
        </Card>

        {/* Forecast Chart */}
        <Card>
          <div className="p-6 border-b border-slate-700/30">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              6-Month Forecast
              <span className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                {forecast?.accuracy_percentage}% Accuracy
              </span>
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Projected emissions with confidence intervals
            </p>
          </div>
          <div className="p-6">
            {forecast ? (
              <ForecastChart forecast={forecast} />
            ) : (
              <div className="flex items-center justify-center py-12 text-slate-500">
                <AlertCircle className="w-5 h-5 mr-2" />
                No forecast data available
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Export Options */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-3">Export Options</h3>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('pdf')}
              loading={exporting}
              icon={<Download className="w-4 h-4" />}
            >
              Export as PDF
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExport('csv')}
              loading={exporting}
              icon={<Download className="w-4 h-4" />}
            >
              Export as CSV
            </Button>
          </div>
          <p className="text-xs text-slate-500 mt-3">
            Exports include all analytics data, trends, and forecasting projections
          </p>
        </div>
      </Card>
    </div>
  )
}
