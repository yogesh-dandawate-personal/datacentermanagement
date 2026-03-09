import { useState, useEffect } from 'react'
import { BarChart3, Zap, TrendingUp, Activity } from 'lucide-react'
import { EnergyDashboard } from './components/EnergyDashboard'

function App() {
  const [apiStatus, setApiStatus] = useState('checking')

  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await fetch('/api/v1/health')
        if (response.ok) {
          setApiStatus('connected')
        } else {
          setApiStatus('error')
        }
      } catch {
        setApiStatus('disconnected')
      }
    }

    checkApi()
    const interval = setInterval(checkApi, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 text-emerald-400" />
            <h1 className="text-2xl font-bold text-white">iNetZero ESG Platform</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${
              apiStatus === 'connected' ? 'bg-emerald-400' :
              apiStatus === 'checking' ? 'bg-yellow-400' :
              'bg-red-400'
            }`} />
            <span className="text-sm text-slate-400">
              API: {apiStatus === 'connected' ? 'Connected' : apiStatus === 'checking' ? 'Checking' : 'Disconnected'}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">Welcome to iNetZero</h2>
          <p className="text-lg text-slate-300 mb-8">
            Monitor, track, and optimize your datacenter's environmental impact with real-time ESG metrics.
          </p>

          {apiStatus === 'disconnected' && (
            <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-8">
              <p className="text-red-200">
                <strong>⚠️ Backend API Not Connected:</strong> Make sure the backend is running.
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-emerald-500 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Total Facilities</p>
                <p className="text-3xl font-bold text-white mt-2">--</p>
              </div>
              <Activity className="w-8 h-8 text-emerald-400" />
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-blue-500 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Total Energy (kWh)</p>
                <p className="text-3xl font-bold text-white mt-2">--</p>
              </div>
              <Zap className="w-8 h-8 text-blue-400" />
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-purple-500 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">Carbon Emissions (kg)</p>
                <p className="text-3xl font-bold text-white mt-2">--</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-400" />
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-orange-500 transition">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium">PUE Score</p>
                <p className="text-3xl font-bold text-white mt-2">--</p>
              </div>
              <BarChart3 className="w-8 h-8 text-orange-400" />
            </div>
          </div>
        </div>

        <div className="mb-12">
          <EnergyDashboard />
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">API Documentation</h3>
          <p className="text-slate-300 mb-4">
            Your backend API provides the following endpoints:
          </p>
          <ul className="space-y-2 text-slate-400 text-sm">
            <li>📊 Energy metrics and dashboards</li>
            <li>📋 Compliance reports and audits</li>
            <li>🔄 Workflow approvals</li>
            <li>📈 Performance tracking and KPIs</li>
            <li>🛡️ Security and backup management</li>
          </ul>
        </div>
      </main>

      <footer className="border-t border-slate-700 bg-slate-900/50 mt-16 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 text-sm">
          <p>© 2026 iNetZero ESG Platform</p>
          <p className="mt-2">Deployed with Docker • Powered by React + FastAPI</p>
        </div>
      </footer>
    </div>
  )
}

export default App
