import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Landing } from './pages/Landing'
import { Dashboard } from './pages/Dashboard'
import { Energy } from './pages/Energy'
import { Reports } from './pages/Reports'
import { Settings } from './pages/Settings'
import { Marketplace } from './pages/Marketplace'
import { Portfolio } from './pages/Portfolio'
import { Trading } from './pages/Trading'
import { Approvals } from './pages/Approvals'
import { Copilot } from './pages/Copilot'
import { Compliance } from './pages/Compliance'
import { Analytics } from './pages/Analytics'
import { Benchmarking } from './pages/Benchmarking'
import { Alerts } from './pages/Alerts'
import { Layout } from './components/Layout'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { ErrorBoundary } from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/energy"
            element={
              <ProtectedRoute>
                <Layout>
                  <Energy />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Layout>
                  <Reports />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <Settings />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/marketplace"
            element={
              <ProtectedRoute>
                <Layout>
                  <Marketplace />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/portfolio"
            element={
              <ProtectedRoute>
                <Layout>
                  <Portfolio />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/trading"
            element={
              <ProtectedRoute>
                <Layout>
                  <Trading />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/approvals"
            element={
              <ProtectedRoute>
                <Layout>
                  <Approvals />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/copilot"
            element={
              <ProtectedRoute>
                <Layout>
                  <Copilot />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/compliance"
            element={
              <ProtectedRoute>
                <Layout>
                  <Compliance />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <Layout>
                  <Analytics />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/benchmarking"
            element={
              <ProtectedRoute>
                <Layout>
                  <Benchmarking />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/alerts"
            element={
              <ProtectedRoute>
                <Layout>
                  <Alerts />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
