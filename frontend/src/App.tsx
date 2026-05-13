import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import RequestsPage from '@/pages/RequestsPage'
import RequestDetailPage from '@/pages/RequestDetailPage'
import CreateRequestPage from '@/pages/CreateRequestPage'
import ConsolidatedReportPage from '@/pages/ConsolidatedReportPage'
import InstitutionsPage from '@/pages/InstitutionsPage'
import InstitutionDetailPage from '@/pages/InstitutionDetailPage'
import MonitoringPage from '@/pages/MonitoringPage'
import ClassifiersPage from '@/pages/ClassifiersPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[#5e6ad2] animate-pulse" />
          <span className="text-sm text-gray-400">Загрузка...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function DirectorRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  if (user?.role !== 'director') {
    return <Navigate to="/dashboard" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Navigate to="/dashboard" replace />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/requests"
        element={
          <ProtectedRoute>
            <RequestsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/requests/new"
        element={
          <ProtectedRoute>
            <DirectorRoute>
              <CreateRequestPage />
            </DirectorRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path="/requests/:id"
        element={
          <ProtectedRoute>
            <RequestDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports/consolidated"
        element={
          <ProtectedRoute>
            <ConsolidatedReportPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/institutions"
        element={
          <ProtectedRoute>
            <InstitutionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/institutions/:id"
        element={
          <ProtectedRoute>
            <InstitutionDetailPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/monitoring"
        element={
          <ProtectedRoute>
            <MonitoringPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/classifiers"
        element={
          <ProtectedRoute>
            <ClassifiersPage />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
