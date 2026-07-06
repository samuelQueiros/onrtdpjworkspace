import { Link } from 'react-router-dom'
import { EmptyState, StatusBadge } from '../../pages/_helpers'
import { formatDate } from '../../utils/formatters'
import { DashboardIcon as Icon } from './DashboardIcons'
import UserDot from './UserDot'

export default function AdminDashboard({ dash, pendentes }) {
  return (
    <>
      {dash.alertas_contabilidade?.length > 0 && (
        <div className="alert alert-warning spaced alert-box">
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
            <span style={{ flexShrink: 0, marginTop: 1 }}>{Icon.alert}</span>
            <div>
              <strong>Alerta de contabilidade - férias nos próximos 4 dias:</strong>
              <ul style={{ marginTop: 6, paddingLeft: 16 }}>
                {dash.alertas_contabilidade.map(alerta => (
                  <li key={alerta.ferias_id}>
                    <strong>{alerta.nome_usuario}</strong>: {formatDate(alerta.data_inicio)} a {formatDate(alerta.data_fim)}
                    {alerta.dias_para_inicio === 0 ? ' - começa hoje!' : ` - em ${alerta.dias_para_inicio} dia(s)`}
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
                {dash.pessoas_em_ferias.map(pessoa => (
                  <li key={pessoa.id} className="people-item">
                    <div className="people-avatar" style={{ background: pessoa.cor || '#0d1b3e' }}>
                      {pessoa.nome?.[0]?.toUpperCase()}
                    </div>
                    <div>
                      <strong>{pessoa.nome}</strong>
                      <div className="muted" style={{ fontSize: 12 }}>
                        até {formatDate(pessoa.data_fim)} - {pessoa.dias_restantes} dia(s) restante(s)
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
                  {dash.proximas_ferias.map(ferias => (
                    <tr key={ferias.id}>
                      <td>
                        <UserDot cor={ferias.cor} nome={ferias.nome_usuario} />
                        {ferias.nome_usuario}
                      </td>
                      <td>{formatDate(ferias.data_inicio)}</td>
                      <td>{formatDate(ferias.data_fim)}</td>
                      <td>{ferias.dias_usados}</td>
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

        <section className="card">
          <div className="card-header"><h2 className="card-title">Central de alertas</h2></div>
          <div className="card-body">
            {dash.alertas_contabilidade?.length > 0 ? (
              <ul className="alert-list">
                {dash.alertas_contabilidade.map(alerta => (
                  <li key={alerta.ferias_id} className="alert-item amber">
                    <span>{Icon.alert}</span>
                    <div>
                      <strong>{alerta.nome_usuario}</strong> - encaminhar à contabilidade
                      <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                        Férias: {formatDate(alerta.data_inicio)} a {formatDate(alerta.data_fim)}
                        {alerta.dias_para_inicio === 0 ? ' (hoje!)' : ` (em ${alerta.dias_para_inicio} dia(s))`}
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
