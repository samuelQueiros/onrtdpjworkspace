import { Link } from 'react-router-dom'
import { formatDate } from '../../utils/formatters'
import { DashboardIcon as Icon } from './DashboardIcons'

function AdminQuickActions({ pendentes = [] }) {
  return (
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
        <Link className="quick-action" to="/configuracoes">
          <strong>Configurações</strong>
          <span>Gerencie cargos, equipes e limites.</span>
        </Link>
      </div>
    </section>
  )
}

function AdminAlertCenter({ alertas = [] }) {
  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Central de alertas</h2></div>
      <div className="card-body">
        {alertas.length > 0 ? (
          <ul className="alert-list">
            {alertas.map(alerta => (
              <li key={alerta.ferias_id} className="alert-item amber">
                <span>{Icon.alert}</span>
                <div>
                  <strong>{alerta.nome_usuario}</strong> - encaminhar à contabilidade
                  <div className="muted-xs">
                    Férias: {formatDate(alerta.data_inicio)} a {formatDate(alerta.data_fim)}
                    {alerta.dias_para_inicio === 0 ? ' (hoje!)' : ` (em ${alerta.dias_para_inicio} dia(s))`}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted p-y-8">Nenhum alerta no momento.</p>
        )}
      </div>
    </section>
  )
}

export default function AdminActionsAndAlerts({ alertas = [], pendentes = [] }) {
  return (
    <div className="grid-2">
      <AdminQuickActions pendentes={pendentes} />
      <AdminAlertCenter alertas={alertas} />
    </div>
  )
}
