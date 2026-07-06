import { EmptyState, StatusBadge } from '../../pages/_helpers'
import { formatDate } from '../../utils/formatters'
import { STATUS_LABEL, STATUS_TONE } from './statusFerias'

export default function TabelaMinhasFerias({ ferias, onCancel, onEdit }) {
  return (
    <section className="card">
      <div className="table-wrap">
        {ferias.length ? (
          <table>
            <thead>
              <tr>
                <th>Início</th>
                <th>Fim</th>
                <th>Dias</th>
                <th>Tipo</th>
                <th>Status</th>
                <th>Motivo</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {ferias.map(item => (
                <tr key={item.id}>
                  <td>{formatDate(item.data_inicio)}</td>
                  <td>{formatDate(item.data_fim)}</td>
                  <td>{item.dias_usados}</td>
                  <td>
                    {item.ferias_acordo
                      ? <StatusBadge tone="blue">Por acordo</StatusBadge>
                      : <StatusBadge tone="gray">Normal</StatusBadge>}
                  </td>
                  <td>
                    <StatusBadge tone={STATUS_TONE[item.status] || 'gray'}>
                      {STATUS_LABEL[item.status] || item.status}
                    </StatusBadge>
                  </td>
                  <td className="muted">{item.motivo_rejeicao || '-'}</td>
                  <td className="actions-cell">
                    {item.status === 'pendente' && (
                      <button className="btn btn-outline btn-sm" onClick={() => onEdit(item)}>
                        Editar
                      </button>
                    )}
                    <button className="btn btn-danger btn-sm" onClick={() => onCancel(item.id)}>
                      Cancelar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title="Sem férias registradas"
            text="Solicite seu primeiro período para iniciar o controle."
          />
        )}
      </div>
    </section>
  )
}
