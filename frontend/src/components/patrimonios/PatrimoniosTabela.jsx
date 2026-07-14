import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { STATUS_LABEL, STATUS_TONE, TIPO_LABEL, identificacaoEquipamento } from './patrimoniosLabels'

export default function PatrimoniosTabela({ data, loading, detailLoadingId, onDetails, onEdit, onPageChange }) {
  const items = data.items || []

  return (
    <section className="card patrimonio-list-card" aria-busy={loading}>
      <div className="card-header patrimonio-list-header">
        <div>
          <h2 className="card-title">Equipamentos cadastrados</h2>
          <p className="muted-xs mt-4">{data.total || 0} registro(s) encontrado(s)</p>
        </div>
        {loading && <div className="spinner" aria-label="Atualizando equipamentos" />}
      </div>

      <div className="table-wrap">
        {loading && !items.length ? (
          <div className="empty" role="status">
            <div className="spinner" />
            <p>Carregando equipamentos...</p>
          </div>
        ) : !items.length ? (
          <EmptyState
            title="Nenhum equipamento encontrado"
            text="Ajuste os filtros ou cadastre o primeiro patrimônio da empresa."
          />
        ) : (
          <table className="patrimonios-table">
            <caption className="sr-only">Lista de equipamentos e vínculos atuais</caption>
            <thead>
              <tr>
                <th>Identificação</th>
                <th>Equipamento</th>
                <th>Série</th>
                <th>Status</th>
                <th>Responsável atual</th>
                <th>Conservação</th>
                <th>Situação</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td><strong>{identificacaoEquipamento(item)}</strong></td>
                  <td>
                    <strong>{TIPO_LABEL[item.tipo] || item.tipo}</strong>
                    <span className="patrimonio-table-sub">{item.marca} {item.modelo}</span>
                  </td>
                  <td>{item.numero_serie || <span className="muted">Não informado</span>}</td>
                  <td>
                    <StatusBadge tone={STATUS_TONE[item.status] || 'gray'}>
                      {STATUS_LABEL[item.status] || item.status}
                    </StatusBadge>
                  </td>
                  <td>{item.vinculo_atual?.user_nome || <span className="muted">Sem vínculo</span>}</td>
                  <td><span className="patrimonio-conservation" title={item.estado_conservacao}>{item.estado_conservacao}</span></td>
                  <td>
                    <StatusBadge tone={item.ativo ? 'green' : 'gray'}>{item.ativo ? 'Ativo' : 'Inativo'}</StatusBadge>
                  </td>
                  <td className="actions-cell">
                    <button
                      className="btn btn-outline btn-sm"
                      type="button"
                      onClick={() => onDetails(item)}
                      disabled={detailLoadingId !== null}
                    >
                      {detailLoadingId === item.id ? 'Abrindo...' : 'Detalhes'}
                    </button>
                    {(item.acoes_permitidas || []).includes('editar') && (
                      <button className="btn btn-outline btn-sm" type="button" onClick={() => onEdit(item)}>Editar</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="patrimonio-pagination" aria-label="Paginação de equipamentos">
        <span>Página {data.page || 1} de {data.pages || 1}</span>
        <div className="button-row">
          <button className="btn btn-outline btn-sm" type="button" disabled={loading || data.page <= 1} onClick={() => onPageChange(data.page - 1)}>Anterior</button>
          <button className="btn btn-outline btn-sm" type="button" disabled={loading || data.page >= data.pages} onClick={() => onPageChange(data.page + 1)}>Próxima</button>
        </div>
      </div>
    </section>
  )
}
