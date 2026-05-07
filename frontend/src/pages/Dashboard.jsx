import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

function AvisoCard({ aviso }) {
  return (
    <div className={`aviso-card${aviso.fixado ? ' aviso-fixado' : ''}`}>
      <div className="aviso-header">
        <strong>{aviso.titulo}</strong>
        {aviso.fixado && <span className="badge badge-amber">Fixado</span>}
      </div>
      <p className="aviso-corpo">{aviso.conteudo}</p>
      <small className="muted">
        Publicado por {aviso.criado_por_nome} em {formatDate(aviso.criado_em)}
        {aviso.data_expiracao && ` · Expira em ${formatDate(aviso.data_expiracao)}`}
      </small>
    </div>
  )
}

export default function Dashboard() {
  const { user, refreshUser } = useAuth()
  const [ferias, setFerias] = useState([])
  const [relatorio, setRelatorio] = useState(null)
  const [avisos, setAvisos] = useState([])
  const [pendentes, setPendentes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const calls = [api.minhasFerias(), refreshUser(), api.listarAvisos()]
    if (user?.role === 'admin') {
      calls.push(api.relatorios())
      calls.push(api.feriasPendentes())
    }
    Promise.all(calls)
      .then(([res, , avisosData, report, pend]) => {
        setFerias(res?.ferias || res || [])
        setAvisos(avisosData || [])
        if (report) setRelatorio(report)
        if (pend) setPendentes(pend)
      })
      .finally(() => setLoading(false))
  }, [])

  const proximas = useMemo(() => {
    const today = new Date()
    const lista = Array.isArray(ferias) ? ferias : (ferias?.ferias || [])
    return lista
      .filter(item => item.status === 'aprovada' && new Date(`${item.data_fim}T23:59:59`) >= today)
      .sort((a, b) => String(a.data_inicio).localeCompare(String(b.data_inicio)))
      .slice(0, 4)
  }, [ferias])

  const usados = user ? user.dias_totais - user.dias_restantes : 0
  const totalColaboradores = relatorio?.colaboradores?.length ?? '-'
  const periodosAdmin = relatorio?.colaboradores?.reduce((sum, col) => sum + col.ferias.length, 0) ?? 0

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title={`Olá, ${user?.nome?.split(' ')[0]}`}
        subtitle="Resumo rápido dos seus saldos e períodos registrados."
        action={<Link className="btn btn-primary" to="/solicitar">Nova solicitação</Link>}
      />

      {user?.role === 'admin' && pendentes.length > 0 && (
        <div className="alert alert-warning spaced">
          <strong>{pendentes.length} solicitação(ões) aguardando aprovação.</strong>{' '}
          <Link to="/aprovacoes">Revisar agora →</Link>
        </div>
      )}

      <section className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Dias restantes</div>
          <div className="stat-value">{user?.dias_restantes}</div>
          <div className="stat-sub">de {user?.dias_totais} dias no ciclo</div>
          <div className="progress-track">
            <div
              className="progress-fill green"
              style={{ width: `${Math.max(0, (user?.dias_restantes / user?.dias_totais) * 100)}%` }}
            />
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias usados</div>
          <div className="stat-value">{usados}</div>
          <div className="stat-sub">dias já registrados no ciclo</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Meus períodos</div>
          <div className="stat-value">{Array.isArray(ferias) ? ferias.length : (ferias?.ferias?.length ?? 0)}</div>
          <div className="stat-sub">solicitações no sistema</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">{user?.role === 'admin' ? 'Colaboradores' : 'Avisos ativos'}</div>
          <div className="stat-value">{user?.role === 'admin' ? totalColaboradores : avisos.length}</div>
          <div className="stat-sub">{user?.role === 'admin' ? `${periodosAdmin} períodos mapeados` : 'no mural'}</div>
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Próximas férias</h2></div>
          <div className="table-wrap">
            {proximas.length ? (
              <table>
                <thead><tr><th>Início</th><th>Fim</th><th>Dias</th><th>Status</th></tr></thead>
                <tbody>
                  {proximas.map(item => (
                    <tr key={item.id}>
                      <td>{formatDate(item.data_inicio)}</td>
                      <td>{formatDate(item.data_fim)}</td>
                      <td>{item.dias_usados}</td>
                      <td><StatusBadge tone="green">Aprovadas</StatusBadge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState title="Nenhum período futuro" text="Quando você registrar férias aprovadas, elas aparecerão aqui." />
            )}
          </div>
        </section>

        <section className="card">
          <div className="card-header"><h2 className="card-title">Atalhos rápidos</h2></div>
          <div className="card-body quick-actions">
            <Link className="quick-action" to="/solicitar">
              <strong>Solicitar férias</strong>
              <span>Escolha um período disponível.</span>
            </Link>
            <Link className="quick-action" to="/disponibilidade">
              <strong>Ver calendário</strong>
              <span>Confira datas bloqueadas.</span>
            </Link>
            <Link className="quick-action" to="/mural">
              <strong>Mural de avisos</strong>
              <span>Comunicados e informações.</span>
            </Link>
            {user?.role === 'admin' && (
              <Link className="quick-action" to="/aprovacoes">
                <strong>Aprovar férias</strong>
                <span>{pendentes.length} pendente(s).</span>
              </Link>
            )}
            {user?.role === 'admin' && (
              <Link className="quick-action" to="/relatorios">
                <strong>Relatórios</strong>
                <span>Analise saldos por colaborador.</span>
              </Link>
            )}
          </div>
        </section>
      </div>

      {avisos.length > 0 && (
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">Mural de avisos</h2>
            <Link className="btn btn-outline btn-sm" to="/mural">Ver todos</Link>
          </div>
          <div className="card-body avisos-lista">
            {avisos.slice(0, 3).map(aviso => (
              <AvisoCard key={aviso.id} aviso={aviso} />
            ))}
          </div>
        </section>
      )}
    </>
  )
}
