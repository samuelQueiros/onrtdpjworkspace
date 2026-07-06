import { Link } from 'react-router-dom'
import { formatDate } from '../../utils/formatters'
import { DashboardIcon as Icon } from './DashboardIcons'

export default function AdminDashboardAlerts({ alertas = [], pendentes = [] }) {
  return (
    <>
      {alertas.length > 0 && (
        <div className="alert alert-warning spaced alert-box">
          <div className="inline-start gap-10">
            <span className="shrink-0 mt-1">{Icon.alert}</span>
            <div>
              <strong>Alerta de contabilidade - férias nos próximos 4 dias:</strong>
              <ul className="admin-alert-list">
                {alertas.map(alerta => (
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
    </>
  )
}
