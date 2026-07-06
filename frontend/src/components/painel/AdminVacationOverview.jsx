import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import { DashboardIcon as Icon } from './DashboardIcons'
import UserDot from './UserDot'

function PessoasEmFerias({ pessoas = [] }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">
          {Icon.sun}
          <span className="dashboard-section-title-icon">Em férias hoje</span>
        </h2>
        <StatusBadge tone={pessoas.length > 0 ? 'green' : 'gray'}>
          {pessoas.length} pessoa(s)
        </StatusBadge>
      </div>
      <div className="card-body">
        {pessoas.length ? (
          <ul className="people-list">
            {pessoas.map(pessoa => (
              <li key={pessoa.id} className="people-item">
                <div className="people-avatar" style={{ background: pessoa.cor || '#0d1b3e' }}>
                  {pessoa.nome?.[0]?.toUpperCase()}
                </div>
                <div>
                  <strong>{pessoa.nome}</strong>
                  <div className="muted text-xs">
                    até {formatDate(pessoa.data_fim)} - {pessoa.dias_restantes} dia(s) restante(s)
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted p-y-8">Nenhum colaborador em férias hoje.</p>
        )}
      </div>
    </section>
  )
}

function ProximasFerias({ ferias = [] }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Próximas férias (30 dias)</h2>
      </div>
      <div className="table-wrap">
        {ferias.length ? (
          <table>
            <thead>
              <tr><th>Colaborador</th><th>Início</th><th>Fim</th><th>Dias</th></tr>
            </thead>
            <tbody>
              {ferias.map(item => (
                <tr key={item.id}>
                  <td>
                    <UserDot cor={item.cor} nome={item.nome_usuario} />
                    {item.nome_usuario}
                  </td>
                  <td>{formatDate(item.data_inicio)}</td>
                  <td>{formatDate(item.data_fim)}</td>
                  <td>{item.dias_usados}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState title="Sem férias nos próximos 30 dias" text="" />
        )}
      </div>
    </section>
  )
}

export default function AdminVacationOverview({ pessoasEmFerias = [], proximasFerias = [] }) {
  return (
    <div className="grid-2">
      <PessoasEmFerias pessoas={pessoasEmFerias} />
      <ProximasFerias ferias={proximasFerias} />
    </div>
  )
}
