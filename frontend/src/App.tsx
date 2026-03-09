import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Landing } from './pages/Landing'
import { Dashboard } from './pages/Dashboard'
import { Layout } from './components/Layout'
import { useState, useEffect } from 'react'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is logged in (from localStorage or session)
    const token = localStorage.getItem('auth_token')
    setIsAuthenticated(!!token)
  }, [])

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />

        {/* Protected Routes */}
        {isAuthenticated ? (
          <>
            <Route
              path="/dashboard"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
              path="/energy"
              element={
                <Layout>
                  <div className="space-y-6">
                    <h1 className="text-3xl font-bold text-white">Energy Management</h1>
                    <div className="p-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl text-center">
                      <p className="text-slate-300">Energy dashboard coming soon</p>
                    </div>
                  </div>
                </Layout>
              }
            />
            <Route
              path="/reports"
              element={
                <Layout>
                  <div className="space-y-6">
                    <h1 className="text-3xl font-bold text-white">Reports</h1>
                    <div className="p-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl text-center">
                      <p className="text-slate-300">Reports dashboard coming soon</p>
                    </div>
                  </div>
                </Layout>
              }
            />
            <Route
              path="/settings"
              element={
                <Layout>
                  <div className="space-y-6">
                    <h1 className="text-3xl font-bold text-white">Settings</h1>
                    <div className="p-8 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl border border-slate-700/50 rounded-2xl text-center">
                      <p className="text-slate-300">Settings coming soon</p>
                    </div>
                  </div>
                </Layout>
              }
            />
          </>
        ) : (
          <Route path="/dashboard" element={<Navigate to="/" replace />} />
        )}

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}

export default App
