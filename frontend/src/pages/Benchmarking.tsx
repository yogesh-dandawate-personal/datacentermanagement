/**
 * Benchmarking Dashboard Page
 * Industry benchmarks, peer comparison, gap analysis, and improvement recommendations
 */

import { useState } from 'react'
import { Download, RefreshCw, Target } from 'lucide-react'
import { useBenchmarking } from '../hooks/useBenchmarking'
import { BenchmarkComparison } from '../components/BenchmarkComparison'
import { ImprovementPlan } from '../components/ImprovementPlan'
import { Button } from '../components/ui/Button'
import { Select } from '../components/ui/Select'
import { Spinner } from '../components/ui/Spinner'
import { Alert } from '../components/ui/Alert'

export function Benchmarking() {
  const [industry, setIndustry] = useState<string>()
  const [exporting, setExporting] = useState(false)

  const {
    benchmarks,
    peerComparison,
    recommendations,
    loading,
    error,
    refetch,
    exportBenchmarks,
  } = useBenchmarking(industry)

  const handleExport = async (format: 'pdf' | 'csv') => {
    setExporting(true)
    try {
      await exportBenchmarks(format)
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
        <span className="ml-3 text-slate-400">Loading benchmarks...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert
          variant="error"
          title="Error Loading Benchmarks"
          message={error}
          action={<Button size="sm" variant="outline" onClick={() => refetch()}>Retry</Button>}
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
            <Target className="w-8 h-8 text-cyan-400" />
            Benchmarking
          </h1>
          <p className="text-slate-400 mt-1">
            Compare performance against industry standards and peers
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Select
            value={industry || ''}
            onChange={(e) => setIndustry(e.target.value || undefined)}
            options={[
              { value: '', label: 'All Industries' },
              { value: 'technology', label: 'Technology' },
              { value: 'manufacturing', label: 'Manufacturing' },
              { value: 'retail', label: 'Retail' },
              { value: 'healthcare', label: 'Healthcare' },
            ]}
          />

          <Button variant="outline" size="md" onClick={() => refetch()} icon={<RefreshCw className="w-4 h-4" />}>
            Refresh
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={() => handleExport('pdf')}
            loading={exporting}
            icon={<Download className="w-4 h-4" />}
          >
            Export
          </Button>
        </div>
      </div>

      {/* Benchmark Comparison */}
      {benchmarks && peerComparison && (
        <BenchmarkComparison benchmarks={benchmarks} peerComparison={peerComparison} />
      )}

      {/* Improvement Plan */}
      <div className="grid grid-cols-1 gap-6">
        <ImprovementPlan recommendations={recommendations} />
      </div>
    </div>
  )
}
