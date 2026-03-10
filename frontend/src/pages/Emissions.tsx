/**
 * Emissions Module - Main Landing Page
 * Provides navigation and quick stats for all emissions features
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Button, Spinner, Alert } from '@/components/ui'
import { Cloud, TrendingDown, Target, AlertTriangle, FileText, Upload, BarChart3 } from 'lucide-react'

export default function EmissionsPage() {
  const navigate = useNavigate()
  const [selectedFacility] = useState<string | null>(null)

  const features = [
    {
      title: 'Facility Dashboard',
      description: 'View real-time emissions data, carbon intensity, and trend analysis',
      icon: BarChart3,
      href: '/emissions/dashboard',
      color: 'text-blue-400',
      status: 'Ready'
    },
    {
      title: 'Data Entry',
      description: 'Submit activity data manually or upload CSV/Excel files',
      icon: Upload,
      href: '/emissions/data-entry',
      color: 'text-green-400',
      status: 'Ready'
    },
    {
      title: 'Reporting Center',
      description: 'Generate ESG reports (GHG Protocol, CDP, GRI, TCFD)',
      icon: FileText,
      href: '/emissions/reports',
      color: 'text-cyan-400',
      status: 'Ready'
    },
    {
      title: 'Reduction Targets',
      description: 'Set and track emissions reduction goals',
      icon: Target,
      href: '/emissions/targets',
      color: 'text-orange-400',
      status: 'Ready'
    },
    {
      title: 'Alerts Center',
      description: 'Manage alert rules and emission thresholds',
      icon: AlertTriangle,
      href: '/emissions/alerts',
      color: 'text-red-400',
      status: 'Ready'
    },
    {
      title: 'Analytics',
      description: 'Deep-dive analysis, benchmarking, and optimization opportunities',
      icon: TrendingDown,
      href: '/emissions/analytics',
      color: 'text-purple-400',
      status: 'Ready'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <Cloud className="w-8 h-8 text-green-400" />
          <h1 className="text-3xl font-bold">Emissions Management</h1>
        </div>
        <p className="text-slate-400">
          Comprehensive emissions tracking and ESG reporting system with Scope 1, 2, 3 calculations
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm text-slate-400">Total Portfolio Emissions</p>
          <p className="text-2xl font-bold">—</p>
          <p className="text-xs text-slate-500 mt-1">MTD</p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Active Alert Rules</p>
          <p className="text-2xl font-bold">—</p>
          <p className="text-xs text-slate-500 mt-1">System-wide</p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Facilities Tracked</p>
          <p className="text-2xl font-bold">—</p>
          <p className="text-xs text-slate-500 mt-1">With data sources</p>
        </Card>

        <Card>
          <p className="text-sm text-slate-400">Reduction Targets</p>
          <p className="text-2xl font-bold">—</p>
          <p className="text-xs text-slate-500 mt-1">Active</p>
        </Card>
      </div>

      {/* Feature Grid */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Module Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature) => {
            const Icon = feature.icon
            return (
              <Card
                key={feature.href}
                className="cursor-pointer hover:border-blue-500/50 transition group"
                onClick={() => navigate(feature.href)}
              >
                <div className="flex items-start justify-between mb-3">
                  <Icon className={`w-6 h-6 ${feature.color} group-hover:scale-110 transition`} />
                  <span className="text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded">
                    {feature.status}
                  </span>
                </div>

                <h3 className="font-semibold mb-2 group-hover:text-white transition">
                  {feature.title}
                </h3>

                <p className="text-sm text-slate-400 mb-4">
                  {feature.description}
                </p>

                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={(e) => {
                    e.stopPropagation()
                    navigate(feature.href)
                  }}
                >
                  Open
                </Button>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Quick Start */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Quick Start</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold flex-shrink-0">
              1
            </div>
            <div>
              <p className="font-medium">Define Emission Sources</p>
              <p className="text-sm text-slate-400">Set up emission sources for each facility (fuel, electricity, etc.)</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold flex-shrink-0">
              2
            </div>
            <div>
              <p className="font-medium">Submit Activity Data</p>
              <p className="text-sm text-slate-400">Enter readings manually or upload CSV files for batch data</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold flex-shrink-0">
              3
            </div>
            <div>
              <p className="font-medium">Calculate Emissions</p>
              <p className="text-sm text-slate-400">Run calculations using EPA factors and GHG Protocol standards</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold flex-shrink-0">
              4
            </div>
            <div>
              <p className="font-medium">Track & Report</p>
              <p className="text-sm text-slate-400">Monitor progress, set targets, and generate compliance reports</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Standards & Compliance */}
      <Card>
        <h2 className="text-xl font-semibold mb-4">Standards & Compliance</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: 'GHG Protocol', desc: 'Corporate Accounting & Reporting Standard' },
            { name: 'ISO 14064', desc: 'Greenhouse Gas Quantification & Reporting' },
            { name: 'CDP', desc: 'Environmental Disclosure Platform' },
            { name: 'TCFD', desc: 'Climate-related Financial Disclosures' }
          ].map((standard) => (
            <div key={standard.name} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50">
              <p className="font-medium text-sm">{standard.name}</p>
              <p className="text-xs text-slate-400 mt-1">{standard.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Documentation */}
      <Card>
        <h2 className="text-xl font-semibold mb-3">Documentation</h2>
        <div className="space-y-2 text-sm">
          <p className="text-slate-400">
            📘 <a href="#" className="text-blue-400 hover:text-blue-300">User Guide</a> - How to use emissions features
          </p>
          <p className="text-slate-400">
            📊 <a href="#" className="text-blue-400 hover:text-blue-300">Calculation Methodology</a> - Detailed formulas and standards
          </p>
          <p className="text-slate-400">
            🔧 <a href="#" className="text-blue-400 hover:text-blue-300">Admin Guide</a> - Configuration and integrations
          </p>
          <p className="text-slate-400">
            ⚙️ <a href="#" className="text-blue-400 hover:text-blue-300">API Documentation</a> - Developer reference
          </p>
        </div>
      </Card>
    </div>
  )
}
