import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading, availabilityError, retrySession } = useAuth()

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
  if (adminOnly && user.role !== 'admin') return <Navigate to="/" replace />

  return children
}
