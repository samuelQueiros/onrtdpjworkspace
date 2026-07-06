import { EmptyState, StatusBadge } from '../../pages/_helpers'
import { formatDate } from '../../utils/formatters'
import HistoricoAprovacao from './HistoricoAprovacao'
import { EMPTY_STATE, FILTER_LABELS, STATUS_LABELS } from './statusAprovacoes'
import UserDot from './UserDot'

export default function TabelaAprovacoes({ ferias, filtro, onAprovar, onRejeitar }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">{FILTER_LABELS[filtro]}</h2>
        <StatusBadge tone={filtro === 'pendente' && ferias.length > 0 ? 'amber' : 'gray'}>
          {ferias.length} registro(s)
        </StatusBadge>
      </div>
      <div className="table-wrap">
        {ferias.length ? (
          <table>
            <thead>
              <tr>
                <th>Colaborador</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Dias</th>
                <th>Tipo</th>
                <th>Status</th>
                <th>Solicitado em</th>
                <th>Histórico</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {ferias.map(item => (
                <tr key={item.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <UserDot cor={item.cor_usuario} nome={item.nome_usuario} />
                      <strong>{item.nome_usuario}</strong>
                    </div>
                  </td>
                  <td>{formatDate(item.data_inicio)}</td>
                  <td>{formatDate(item.data_fim)}</td>
                  <td>{item.dias_usados}</td>
                  <td>
                    {item.ferias_acordo
                      ? <StatusBadge tone="blue">Por acordo</StatusBadge>
                      : <StatusBadge tone="gray">Normal</StatusBadge>}
                  </td>
                  <td>
                    <StatusBadge tone={STATUS_LABELS[item.status]?.tone || 'gray'}>
                      {STATUS_LABELS[item.status]?.label || item.status}
                    </StatusBadge>
                  </td>
                  <td>{formatDate(item.criado_em)}</td>
                  <td><HistoricoAprovacao ferias={item} /></td>
                  <td className="actions-cell">
                    {item.status === 'pendente' ? (
                      <>
                        <button className="btn btn-primary btn-sm" onClick={() => onAprovar(item.id)}>
                          Aprovar
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => onRejeitar(item)}>
                          Rejeitar
                        </button>
                      </>
                    ) : (
                      <span className="muted" style={{ fontSize: 12 }}>-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title={EMPTY_STATE[filtro]}
            text={
              filtro === 'pendente'
                ? 'Quando colaboradores enviarem solicitações, elas aparecerão aqui.'
                : 'Utilize os filtros para visualizar outros status.'
            }
          />
        )}
      </div>
    </section>
  )
}
