import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

export default function Dashboard() {
  const { user, refreshUser } = useAuth()
  const [ferias, setFerias] = useState([])
  const [relatorio, setRelatorio] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const calls = [api.minhasFerias(), refreshUser()]
    if (user?.role === 'admin') calls.push(api.relatorios())
    Promise.all(calls)
      .then(([items, , report]) => {
        setFerias(items)
        if (report) setRelatorio(report)
      })
      .finally(() => setLoading(false))
  }, [])

  const proximas = useMemo(() => {
    const today = new Date()
    return ferias
      .filter(item => new Date(`${item.data_fim}T23:59:59`) >= today)
      .sort((a, b) => String(a.data_inicio).localeCompare(String(b.data_inicio)))
      .slice(0, 4)
  }, [ferias])

  const usados = user ? user.dias_totais - user.dias_restantes : 0
  const totalColaboradores = relatorio?.colaboradores?.length ?? '-'
  const periodosAdmin = relatorio?.colaboradores?.reduce((sum, col) => sum + col.ferias.length, 0) ?? ferias.length

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title={`Ola, ${user?.nome}`}
        subtitle="Resumo rapido dos seus saldos e periodos registrados."
        action={<Link className="btn btn-primary" to="/solicitar">Nova solicitacao</Link>}
      />

      <section className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Dias restantes</div>
          <div className="stat-value">{user?.dias_restantes}</div>
          <div className="stat-sub">de {user?.dias_totais} dias no ciclo</div>
          <div className="progress-track"><div className="progress-fill green" style={{ width: `${Math.max(0, (user?.dias_restantes / user?.dias_totais) * 100)}%` }} /></div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias usados</div>
          <div className="stat-value">{usados}</div>
          <div className="stat-sub">dias ja registrados</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Meus periodos</div>
          <div className="stat-value">{ferias.length}</div>
          <div className="stat-sub">solicitacoes no sistema</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">{user?.role === 'admin' ? 'Colaboradores' : 'Periodo geral'}</div>
          <div className="stat-value">{user?.role === 'admin' ? totalColaboradores : periodosAdmin}</div>
          <div className="stat-sub">{user?.role === 'admin' ? `${periodosAdmin} periodos mapeados` : 'acompanhe no calendario'}</div>
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Proximas ferias</h2></div>
          <div className="table-wrap">
            {proximas.length ? (
              <table>
                <thead><tr><th>Inicio</th><th>Fim</th><th>Dias</th><th>Status</th></tr></thead>
                <tbody>
                  {proximas.map(item => (
                    <tr key={item.id}>
                      <td>{formatDate(item.data_inicio)}</td>
                      <td>{formatDate(item.data_fim)}</td>
                      <td>{item.dias_usados}</td>
                      <td><StatusBadge tone="green">Registrado</StatusBadge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <EmptyState title="Nenhum periodo futuro" text="Quando voce registrar ferias, elas aparecerao aqui." />}
          </div>
        </section>

        <section className="card">
          <div className="card-header"><h2 className="card-title">Atalhos</h2></div>
          <div className="card-body quick-actions">
            <Link className="quick-action" to="/solicitar"><strong>Solicitar ferias</strong><span>Escolha um periodo disponivel.</span></Link>
            <Link className="quick-action" to="/disponibilidade"><strong>Ver calendario</strong><span>Confira datas bloqueadas.</span></Link>
            {user?.role === 'admin' && <Link className="quick-action" to="/relatorios"><strong>Relatorios</strong><span>Analise saldos por colaborador.</span></Link>}
          </div>
        </section>
      </div>
    </>
  )
}
