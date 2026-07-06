import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AdminDashboard from '../components/painel/AdminDashboard'
import UserDashboard from '../components/painel/UserDashboard'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from './_helpers'

export default function Dashboard() {
  const { user, refreshUser } = useAuth()
  const [ferias, setFerias] = useState([])
  const [avisos, setAvisos] = useState([])
  const [pendentes, setPendentes] = useState([])
  const [dash, setDash] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const calls = [api.minhasFerias(), refreshUser(), api.listarAvisos()]
    if (user?.role === 'admin') {
      calls.push(api.feriasPendentes())
      calls.push(api.dashboard())
    }
    Promise.all(calls)
      .then(([res, , avisosData, pend, dashData]) => {
        setFerias(res?.ferias || res || [])
        setAvisos(avisosData || [])
        if (pend) setPendentes(pend)
        if (dashData) setDash(dashData)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title={`Olá, ${user?.nome?.split(' ')[0]}`}
        subtitle={
          user?.role === 'admin'
            ? 'Painel administrativo - visão geral do sistema de Gestão RH.'
            : 'Resumo rápido dos seus saldos e períodos registrados.'
        }
        action={<Link className="btn btn-primary" to="/solicitar">Nova solicitação</Link>}
      />

      {user?.role === 'admin' && dash ? (
        <AdminDashboard dash={dash} pendentes={pendentes} />
      ) : (
        <UserDashboard user={user} ferias={ferias} avisos={avisos} />
      )}
    </>
  )
}
