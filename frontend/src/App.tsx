import { ReactNode, useEffect, useState } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'
import AnalyticsPage from './pages/AnalyticsPage'
import BranchManagementPage from './pages/BranchManagementPage'
import CompliancePage from './pages/CompliancePage'
import GrowthTrackingPage from './pages/GrowthTrackingPage'
import OfficerDashboardPage from './pages/OfficerDashboardPage'
import RiskManagementPage from './pages/RiskManagementPage'
import RegionalViewPage from './pages/RegionalViewPage'
import UploadDataPage from './pages/UploadDataPage'
import SignInPage from './pages/SignInPage'
import { fetchAuthJson } from './services/api'

type SessionUser = {
  username?: string
  full_name?: string
  role?: string
}

type AppRole = 'admin' | 'risk' | 'branch-manager' | 'loan-officer' | 'unknown'

type DashboardMetrics = {
  branchesMonitored: number
  totalPar: number
  nplRatio: number
  activeOfficers: number
}

const getSessionUserFromStorage = (): SessionUser | null => {
  const rawUser = window.localStorage.getItem('ai-portfolio-user')
  if (!rawUser) {
    return null
  }

  try {
    return JSON.parse(rawUser) as SessionUser
  } catch {
    return null
  }
}

const getCurrentRole = (): AppRole => {
  const role = getSessionUserFromStorage()?.role
  if (role === 'admin' || role === 'risk' || role === 'branch-manager' || role === 'loan-officer') {
    return role
  }
  return 'unknown'
}

const hasRoleAccess = (role: AppRole, allowedRoles: AppRole[]): boolean => {
  return allowedRoles.includes(role)
}

function ProtectedRoute({ children, allowedRoles }: { children: ReactNode; allowedRoles?: AppRole[] }) {
  const token = window.localStorage.getItem('ai-portfolio-token')
  if (!token) {
    return <Navigate to="/signin" replace />
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role = getCurrentRole()
    if (!hasRoleAccess(role, allowedRoles)) {
      return <Navigate to="/" replace />
    }
  }

  return <>{children}</>
}

function DashboardHome() {
  const navigate = useNavigate()
  const [sessionUser, setSessionUser] = useState<SessionUser | null>(null)
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    branchesMonitored: 0,
    totalPar: 0,
    nplRatio: 0,
    activeOfficers: 0,
  })
  const [metricsLoading, setMetricsLoading] = useState(true)
  const [metricsError, setMetricsError] = useState<string | null>(null)

  useEffect(() => {
    setSessionUser(getSessionUserFromStorage())
  }, [])

  const role = (sessionUser?.role as AppRole | undefined) ?? 'unknown'
  const canViewAnalytics = hasRoleAccess(role, ['admin', 'risk'])
  const canViewBranches = hasRoleAccess(role, ['admin', 'risk', 'branch-manager'])
  const canViewOfficers = hasRoleAccess(role, ['admin', 'risk', 'branch-manager', 'loan-officer'])
  const canViewGrowth = hasRoleAccess(role, ['admin', 'risk'])
  const canViewRisk = hasRoleAccess(role, ['admin', 'risk'])
  const canViewRegional = hasRoleAccess(role, ['admin', 'risk', 'branch-manager'])
  const canViewCompliance = hasRoleAccess(role, ['admin', 'risk'])
  const canUpload = hasRoleAccess(role, ['admin', 'risk', 'branch-manager', 'loan-officer'])

  const handleSignOut = () => {
    window.localStorage.removeItem('ai-portfolio-token')
    window.localStorage.removeItem('ai-portfolio-user')
    navigate('/signin', { replace: true })
  }

  const fetchDashboardMetrics = async () => {
    setMetricsLoading(true)
    setMetricsError(null)

    try {
      const [parData, nplData, branchData, officerData] = await Promise.all([
        fetchAuthJson<{ total_par?: number }>('/par/summary'),
        fetchAuthJson<{ npl_ratio?: number }>('/npl/summary'),
        fetchAuthJson<{ branches?: Array<unknown> }>('/branches/summary'),
        fetchAuthJson<{ total_officers?: number; officers?: Array<unknown> }>('/officers/summary'),
      ])

      setMetrics({
        branchesMonitored: Array.isArray(branchData?.branches) ? branchData.branches.length : 0,
        totalPar: Number(parData?.total_par ?? 0),
        nplRatio: Number(nplData?.npl_ratio ?? 0),
        activeOfficers: Number(officerData?.total_officers ?? officerData?.officers?.length ?? 0),
      })
    } catch (error) {
      setMetricsError(String(error instanceof Error ? error.message : error))
    } finally {
      setMetricsLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardMetrics()
  }, [])

  return (
    <div className="container">
      <header className="header dashboard-hero">
        <div className="hero-badge">Client Experience Platform</div>
        <div className="hero-content">
          <div className="hero-copy">
            <h1>AI Portfolio Analytics Dashboard</h1>
            <p className="subtitle">
              A polished, decision-ready workspace for loan monitoring, portfolio health, and data ingestion.
            </p>
            <div className="header-actions">
              {canUpload && (
                <button className="header-action-button" onClick={() => navigate('/upload')}>
                  Upload Data
                </button>
              )}
              {canViewAnalytics && (
                <button className="header-action-button header-action-secondary" onClick={() => navigate('/analytics')}>
                  Open Analytics
                </button>
              )}
              <button className="header-action-button header-action-secondary" onClick={fetchDashboardMetrics}>
                Refresh metrics
              </button>
              <button className="header-action-button header-action-secondary" onClick={handleSignOut}>
                Sign out
              </button>
            </div>
          </div>

          <div className="hero-panel">
            <div className="hero-user">
              <span className="hero-user-label">Signed in as</span>
              <strong>{sessionUser?.full_name || sessionUser?.username || 'Unknown user'}</strong>
              <span className="hero-user-role">{sessionUser?.role || 'role not set'}</span>
            </div>
            {metricsError && <span className="hero-metrics-warning">{metricsError}</span>}
            <div className="hero-panel-metrics">
              <article>
                <strong>{metricsLoading ? '...' : metrics.branchesMonitored}</strong>
                <span>Branches monitored</span>
              </article>
              <article>
                <strong>{metricsLoading ? '...' : `${metrics.totalPar.toFixed(1)}%`}</strong>
                <span>Total PAR</span>
              </article>
              <article>
                <strong>{metricsLoading ? '...' : `${metrics.nplRatio.toFixed(1)}%`}</strong>
                <span>NPL ratio</span>
              </article>
              <article>
                <strong>{metricsLoading ? '...' : metrics.activeOfficers}</strong>
                <span>Active officers</span>
              </article>
            </div>
          </div>
        </div>
      </header>

      <main className="main">
        <section className="section-headline">
          <div>
            <div className="section-label">Workspace</div>
            <h2>What the client can do</h2>
          </div>
          <p>Clear navigation, quick actions, and a data upload flow optimized for first-time users.</p>
        </section>

        <div className="features-grid">
          {canViewAnalytics && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/analytics')}>
              <h3>📊 Analytics</h3>
              <p>Portfolio risk analysis and performance metrics</p>
              <span className="feature-link">Open Analytics</span>
            </button>
          )}
          {canViewBranches && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/branches')}>
              <h3>🏦 Branch Management</h3>
              <p>Monitor branch performance and operations</p>
              <span className="feature-link">Open Branch Management</span>
            </button>
          )}
          {canViewOfficers && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/officers')}>
              <h3>👥 Officer Dashboard</h3>
              <p>Loan officer performance tracking</p>
              <span className="feature-link">Open Officer Dashboard</span>
            </button>
          )}
          {canViewGrowth && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/growth')}>
              <h3>📈 Growth Tracking</h3>
              <p>Portfolio growth and financial indicators</p>
              <span className="feature-link">Open Growth Tracking</span>
            </button>
          )}
          {canViewRisk && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/risk')}>
              <h3>🚨 Risk Management</h3>
              <p>PAR, NPL, and portfolio health metrics</p>
              <span className="feature-link">Open Risk Management</span>
            </button>
          )}
          {canViewRegional && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/regional')}>
              <h3>🌍 Regional View</h3>
              <p>Geographic distribution and regional analysis</p>
              <span className="feature-link">Open Regional View</span>
            </button>
          )}
          {canViewCompliance && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/compliance')}>
              <h3>🗂 Compliance</h3>
              <p>Audit trails, overrides, and governance controls</p>
              <span className="feature-link">Open Compliance</span>
            </button>
          )}
          {canUpload && (
            <button className="feature-card feature-card-button" onClick={() => navigate('/upload')}>
              <h3>⬆ Upload Data</h3>
              <p>Upload CSV or Excel portfolio files for validation and scoring</p>
              <span className="feature-link">Open Upload</span>
            </button>
          )}
        </div>

        <section className="api-info api-info-grid">
          <div>
            <div className="section-label">Data intake</div>
            <h2>Upload files in one click</h2>
            <p>
              Start from the Upload Data page to submit CSV or Excel portfolio files and validate them against the
              backend sample template.
            </p>
            {canUpload && (
              <button className="upload-callout" onClick={() => navigate('/upload')}>
                Go to upload flow
              </button>
            )}
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>&copy; 2024 AI Portfolio Analytics Dashboard. All rights reserved.</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<ProtectedRoute><DashboardHome /></ProtectedRoute>} />
      <Route path="/signin" element={<SignInPage />} />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk']}>
            <AnalyticsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/branches"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk', 'branch-manager']}>
            <BranchManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/growth"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk']}>
            <GrowthTrackingPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/officers"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk', 'branch-manager', 'loan-officer']}>
            <OfficerDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/risk"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk']}>
            <RiskManagementPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/compliance"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk']}>
            <CompliancePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/regional"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk', 'branch-manager']}>
            <RegionalViewPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <ProtectedRoute allowedRoles={['admin', 'risk', 'branch-manager', 'loan-officer']}>
            <UploadDataPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App