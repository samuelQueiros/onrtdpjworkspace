import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading, availabilityError, retrySession } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <span>Carregando...</span>
      </div>
    )
  }

  if (availabilityError) {
    return (
      <div className="loading-screen" role="alert">
        <strong>Servidor indisponível</strong>
        <span>{availabilityError}</span>
        <button className="btn btn-primary" type="button" onClick={retrySession}>Tentar novamente</button>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />
  if (user.must_change_password && location.pathname !== '/alterar-senha') {
    return <Navigate to="/alterar-senha" replace />
  }
  if (!user.must_change_password && location.pathname === '/alterar-senha') {
    return <Navigate to="/" replace />
  }
  if (adminOnly && user.role !== 'admin') return <Navigate to="/" replace />

  return children
}
