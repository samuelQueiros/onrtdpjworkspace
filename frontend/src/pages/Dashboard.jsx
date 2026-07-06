import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { EmptyState, LoadingCard, PageHeader, StatusBadge } from './_helpers'
import { formatDate } from '../utils/formatters'

const Icon = {
  users: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  check: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><polyline points="20 6 9 17 4 12"/></svg>,
  clock: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
  x: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  building: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>,
  sun: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>,
  alert: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
}

function UserDot({ cor, nome, size = 10 }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: size,
        height: size,
        borderRadius: '50%',
        background: cor || '#64748b',
        marginRight: 6,
        flexShrink: 0,
        verticalAlign: 'middle',
      }}
      title={nome}
    />
  )
}

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

function AdminDashboard({ dash, pendentes }) {
  return (
    <>
      {/* Alertas de contabilidade */}
      {dash.alertas_contabilidade?.length > 0 && (
        <div className="alert alert-warning spaced alert-box">
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            <span style={{ flexShrink: 0, marginTop: 1 }}>{Icon.alert}</span>
            <div>
              <strong>Alerta de contabilidade — férias nos próximos 4 dias:</strong>
              <ul style={{ marginTop: 6, paddingLeft: 16 }}>
                {dash.alertas_contabilidade.map(a => (
                  <li key={a.ferias_id}>
                    <strong>{a.nome_usuario}</strong>: {formatDate(a.data_inicio)} a {formatDate(a.data_fim)}
                    {a.dias_para_inicio === 0 ? ' — começa hoje!' : ` — em ${a.dias_para_inicio} dia(s)`}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {pendentes.length > 0 && (
        <div className="alert alert-warning spaced">
          <strong>{pendentes.length} solicitação(ões) aguardando aprovação.</strong>{' '}
          <Link to="/aprovacoes">Revisar agora →</Link>
        </div>
      )}

      {/* Cards principais */}
      <section className="stat-grid">
        <div className="stat-card">
          <div className="stat-icon-row">
            <div className="stat-label">Colaboradores</div>
            <div className="stat-icon-box navy">{Icon.users}</div>
          </div>
          <div className="stat-value">{dash.total_colaboradores}</div>
          <div className="stat-sub">{dash.total_departamentos} departamento(s)</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-row">
            <div className="stat-label">Aprovadas</div>
            <div className="stat-icon-box green">{Icon.check}</div>
          </div>
          <div className="stat-value">{dash.total_ferias_aprovadas}</div>
          <div className="stat-sub">períodos aprovados</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-row">
            <div className="stat-label">Pendentes</div>
            <div className="stat-icon-box amber">{Icon.clock}</div>
          </div>
          <div className="stat-value">{dash.total_ferias_pendentes}</div>
          <div className="stat-sub">aguardando revisão</div>
          {dash.total_ferias_pendentes > 0 && (
            <div style={{ marginTop: 8 }}>
              <Link className="btn btn-outline btn-sm" to="/aprovacoes">Revisar →</Link>
            </div>
          )}
        </div>
        <div className="stat-card">
          <div className="stat-icon-row">
            <div className="stat-label">Rejeitadas</div>
            <div className="stat-icon-box red">{Icon.x}</div>
          </div>
          <div className="stat-value">{dash.total_ferias_rejeitadas}</div>
          <div className="stat-sub">solicitações negadas</div>
        </div>
      </section>

      <div className="grid-2">
        {/* Pessoas em férias hoje */}
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">
              {Icon.sun}
              <span style={{ marginLeft: 6 }}>Em férias hoje</span>
            </h2>
            <StatusBadge tone={dash.pessoas_em_ferias?.length > 0 ? 'green' : 'gray'}>
              {dash.pessoas_em_ferias?.length ?? 0} pessoa(s)
            </StatusBadge>
          </div>
          <div className="card-body">
            {dash.pessoas_em_ferias?.length ? (
              <ul className="people-list">
                {dash.pessoas_em_ferias.map(p => (
                  <li key={p.id} className="people-item">
                    <div className="people-avatar" style={{ background: p.cor || '#0d1b3e' }}>
                      {p.nome?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <strong>{p.nome}</strong>
                      <div className="muted" style={{ fontSize: 12 }}>
                        até {formatDate(p.data_fim)} — {p.dias_restantes} dia(s) restante(s)
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted" style={{ padding: '8px 0' }}>Nenhum colaborador em férias hoje.</p>
            )}
          </div>
        </section>

        {/* Próximas férias */}
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">Próximas férias (30 dias)</h2>
          </div>
          <div className="table-wrap">
            {dash.proximas_ferias?.length ? (
              <table>
                <thead>
                  <tr><th>Colaborador</th><th>Início</th><th>Fim</th><th>Dias</th></tr>
                </thead>
                <tbody>
                  {dash.proximas_ferias.map(f => (
                    <tr key={f.id}>
                      <td>
                        <UserDot cor={f.cor} nome={f.nome_usuario} />
                        {f.nome_usuario}
                      </td>
                      <td>{formatDate(f.data_inicio)}</td>
                      <td>{formatDate(f.data_fim)}</td>
                      <td>{f.dias_usados}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState title="Sem férias nos próximos 30 dias" text="" />
            )}
          </div>
        </section>
      </div>

      <div className="grid-2">
        {/* Atalhos */}
        <section className="card">
          <div className="card-header"><h2 className="card-title">Atalhos rápidos</h2></div>
          <div className="card-body quick-actions">
            <Link className="quick-action" to="/aprovacoes">
              <strong>Aprovar férias</strong>
              <span>{pendentes.length} pendente(s) aguardando.</span>
            </Link>
            <Link className="quick-action" to="/usuarios">
              <strong>Usuários</strong>
              <span>Gerenciar colaboradores.</span>
            </Link>
            <Link className="quick-action" to="/bloqueios">
              <strong>Bloqueio de datas</strong>
              <span>Impedir férias em períodos críticos.</span>
            </Link>
            <Link className="quick-action" to="/relatorios">
              <strong>Relatórios</strong>
              <span>Analise saldos por colaborador.</span>
            </Link>
            <Link className="quick-action" to="/disponibilidade">
              <strong>Calendário</strong>
              <span>Visualizar férias marcadas.</span>
            </Link>
            <Link className="quick-action" to="/departamentos">
              <strong>Departamentos</strong>
              <span>Gerencie equipes e limites.</span>
            </Link>
          </div>
        </section>

        {/* Alertas */}
        <section className="card">
          <div className="card-header"><h2 className="card-title">Central de alertas</h2></div>
          <div className="card-body">
            {dash.alertas_contabilidade?.length > 0 ? (
              <ul className="alert-list">
                {dash.alertas_contabilidade.map(a => (
                  <li key={a.ferias_id} className="alert-item amber">
                    <span>{Icon.alert}</span>
                    <div>
                      <strong>{a.nome_usuario}</strong> — encaminhar à contabilidade
                      <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                        Férias: {formatDate(a.data_inicio)} a {formatDate(a.data_fim)}
                        {a.dias_para_inicio === 0 ? ' (hoje!)' : ` (em ${a.dias_para_inicio} dia(s))`}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted" style={{ padding: '8px 0' }}>Nenhum alerta no momento.</p>
            )}
          </div>
        </section>
      </div>
    </>
  )
}

function UserDashboard({ user, ferias, avisos }) {
  const usados = user ? user.dias_totais - user.dias_restantes : 0

  const proximas = useMemo(() => {
    const today = new Date()
    const lista = Array.isArray(ferias) ? ferias : (ferias?.ferias || [])
    return lista
      .filter(item => item.status === 'aprovada' && new Date(`${item.data_fim}T23:59:59`) >= today)
      .sort((a, b) => String(a.data_inicio).localeCompare(String(b.data_inicio)))
      .slice(0, 4)
  }, [ferias])

  return (
    <>
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
          <div className="stat-label">Avisos ativos</div>
          <div className="stat-value">{avisos.length}</div>
          <div className="stat-sub">no mural</div>
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
                      <td><StatusBadge tone="green">Aprovada</StatusBadge></td>
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
            <Link className="quick-action" to="/minhas-ferias">
              <strong>Minhas férias</strong>
              <span>Histórico de solicitações.</span>
            </Link>
            <Link className="quick-action" to="/mural">
              <strong>Mural de avisos</strong>
              <span>Comunicados e informações.</span>
            </Link>
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
            ? 'Painel administrativo — visão geral do sistema de Gestão RH.'
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
