import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import FiltrosBloqueios from './FiltrosBloqueios'

export default function BloqueiosTabela({ bloqueios, filtro, filtrados, onDelete, onEdit, onFilterChange }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Períodos cadastrados</h2>
        <FiltrosBloqueios bloqueios={bloqueios} filtro={filtro} onChange={onFilterChange} />
      </div>
      <div className="table-wrap">
        {filtrados.length ? (
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Motivo</th>
                <th>Criado por</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtrados.map(bloqueio => (
                <tr key={bloqueio.id}>
                  <td>
                    <StatusBadge tone={bloqueio.tipo === 'recesso' ? 'blue' : 'red'}>
                      {bloqueio.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                    </StatusBadge>
                  </td>
                  <td>{formatDate(bloqueio.data_inicio)}</td>
                  <td>{formatDate(bloqueio.data_fim)}</td>
                  <td><strong>{bloqueio.motivo}</strong></td>
                  <td>{bloqueio.criado_por_nome || <span className="muted">-</span>}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" onClick={() => onEdit(bloqueio)}>
                      Editar
                    </button>
                    <button className="btn btn-danger btn-sm" onClick={() => onDelete(bloqueio.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title="Nenhum período cadastrado"
            text="Cadastre bloqueios para impedir marcação de férias em datas críticas."
          />
        )}
      </div>
    </section>
  )
}
