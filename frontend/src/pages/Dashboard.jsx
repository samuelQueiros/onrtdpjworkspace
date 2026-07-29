import { useEffect, useState } from 'react'
import '../styles/pages/dashboard.css'
import { Link } from 'react-router-dom'
import AdminDashboard from '../components/painel/AdminDashboard'
import UserDashboard from '../components/painel/UserDashboard'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useToast } from '../contexts/ToastContext'

export default function Dashboard() {
  const { user, refreshUser } = useAuth()
  const toast = useToast()
  const [ferias, setFerias] = useState([])
  const [avisos, setAvisos] = useState([])
  const [pendentes, setPendentes] = useState({ ferias: 0, equipamentos: 0, total: 0 })
  const [dash, setDash] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState('')

  useEffect(() => {
    let active = true
    const load = async () => {
      const baseResults = await Promise.allSettled([
        api.minhasFerias(),
        refreshUser(),
        api.listarAvisos(),
      ])
      if (!active) return
      if (baseResults[0].status === 'fulfilled') {
        setFerias(baseResults[0].value || [])
      }
      if (baseResults[2].status === 'fulfilled') setAvisos(baseResults[2].value || [])

      if (user?.role === 'admin') {
        const [pendingResult, dashboardResult] = await Promise.allSettled([
          api.pendenciasAprovacoes(),
          api.dashboard(),
        ])
        if (!active) return
        if (dashboardResult.status === 'fulfilled') {
          const dashboardData = dashboardResult.value
          setDash(dashboardData)
          if (pendingResult.status === 'fulfilled') {
            setPendentes(pendingResult.value)
          } else {
            const feriasPendentes = dashboardData.total_ferias_pendentes || 0
            const equipamentosPendentes = dashboardData.total_autorizacoes_equipamentos_pendentes || 0
            setPendentes({
              ferias: feriasPendentes,
              equipamentos: equipamentosPendentes,
              total: feriasPendentes + equipamentosPendentes,
            })
          }
        } else {
          setDashboardError(dashboardResult.reason?.message || 'Não foi possível carregar o painel administrativo.')
        }
      }

      const failedBase = baseResults.find(result => result.status === 'rejected')
      if (failedBase) toast.error(failedBase.reason?.message || 'Alguns dados do painel não puderam ser carregados.')
    }

    load().finally(() => active && setLoading(false))
    return () => { active = false }
  }, [refreshUser, toast, user?.role])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title={`Olá, ${user?.nome?.split(' ')[0]}`}
        subtitle={
          user?.role === 'admin'
            ? 'Painel administrativo - visão geral do sistema de Gestão.'
            : 'Resumo rápido dos seus saldos e períodos registrados.'
        }
        action={<Link className="btn btn-primary" to="/solicitar">Nova solicitação</Link>}
      />

      {user?.role === 'admin' ? (dash ? (
        <AdminDashboard dash={dash} pendentes={pendentes} />
      ) : (
        <section className="card">
          <div className="empty" role="alert">
            <h3>Painel administrativo indisponível</h3>
            <p>{dashboardError}</p>
          </div>
        </section>
      )) : (
        <UserDashboard user={user} ferias={ferias} avisos={avisos} />
      )}
    </>
  )
}
