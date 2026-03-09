import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Landing } from './pages/Landing'
import { Dashboard } from './pages/Dashboard'
import { Energy } from './pages/Energy'
import { Reports } from './pages/Reports'
import { Settings } from './pages/Settings'
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
                  <Energy />
                </Layout>
              }
            />
            <Route
              path="/reports"
              element={
                <Layout>
                  <Reports />
                </Layout>
              }
            />
            <Route
              path="/settings"
              element={
                <Layout>
                  <Settings />
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
