/**
 * Emissions Module - Main Container
 * Routes to Emissions sub-pages: Dashboard, Data Entry, Reporting, Targets, Alerts
 */

import { useState } from 'react'
import { Cloud, BarChart3, Upload, Target, Bell } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'

interface EmissionsTab {
  id: string
  label: string
  icon: React.ComponentType<any>
  color: string
}

const emissionsTabs: EmissionsTab[] = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3, color: 'text-cyan-400' },
  { id: 'data-entry', label: 'Data Entry', icon: Upload, color: 'text-blue-400' },
  { id: 'reporting', label: 'Reporting', icon: Cloud, color: 'text-green-400' },
  { id: 'targets', label: 'Targets', icon: Target, color: 'text-yellow-400' },
  { id: 'alerts', label: 'Alerts', icon: Bell, color: 'text-red-400' },
]

export function Emissions() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-2">
            <Cloud className="w-8 h-8 text-green-400" />
            Emissions Management
          </h1>
          <p className="text-slate-400 mt-1">GHG Protocol Scope 1, 2 & 3 Tracking & Reporting</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-700/50 pb-4">
        {emissionsTabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                activeTab === tab.id
                  ? 'bg-green-600/20 border border-green-500/50 text-white'
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Content */}
      <Card>
        <div className="p-12 text-center">
          <Cloud className="w-16 h-16 text-green-400 mx-auto mb-4 opacity-50" />
          <h2 className="text-2xl font-semibold text-white mb-2">
            {emissionsTabs.find(t => t.id === activeTab)?.label}
          </h2>
          <p className="text-slate-400 mb-6">
            {activeTab === 'dashboard' && 'Monitor emissions trends and sustainability metrics'}
            {activeTab === 'data-entry' && 'Submit activity data manually or in bulk'}
            {activeTab === 'reporting' && 'Generate ESG and compliance reports'}
            {activeTab === 'targets' && 'Track progress toward reduction targets'}
            {activeTab === 'alerts' && 'Configure and manage emissions alerts'}
          </p>

          <div className="inline-block">
            <Badge variant="info" className="px-4 py-2">
              Emissions Tracking Ready
            </Badge>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <p className="text-sm text-slate-400 mb-2">GHG Protocol</p>
              <p className="text-lg font-semibold text-white">Scope 1, 2, 3</p>
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <p className="text-sm text-slate-400 mb-2">Data Sources</p>
              <p className="text-lg font-semibold text-white">Multiple Inputs</p>
            </div>
            <div className="p-4 bg-slate-800/50 rounded-lg">
              <p className="text-sm text-slate-400 mb-2">Compliance</p>
              <p className="text-lg font-semibold text-white">TCFD Ready</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}
