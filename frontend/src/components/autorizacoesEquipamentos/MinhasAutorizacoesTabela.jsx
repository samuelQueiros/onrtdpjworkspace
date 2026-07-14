import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatDateTime } from '../../utils/formatters'
import { STATUS_AUTORIZACAO } from './statusAutorizacoes'

export default function MinhasAutorizacoesTabela({ items, onCancel, onDetails }) {
  if (!items.length) {
    return (
      <section className="card">
        <EmptyState title="Nenhuma autorização" text="Suas solicitações de equipamento aparecerão aqui." />
      </section>
    )
  }

  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Histórico de autorizações</h2></div>
      <div className="table-wrap">
        <table>
          <caption className="sr-only">Histórico das solicitações de autorização de equipamentos</caption>
          <thead>
            <tr><th>Número</th><th>Tipo</th><th>Itens</th><th>Status</th><th>Solicitada em</th><th>Ações</th></tr>
          </thead>
          <tbody>
            {items.map(item => {
              const status = STATUS_AUTORIZACAO[item.status] || { label: item.status, tone: 'gray' }
              return (
                <tr key={item.id}>
                  <td>#{item.id}</td>
                  <td>{item.tipo_solicitacao === 'item_diferente' ? 'Equipamento diferente' : 'Itens vinculados'}</td>
                  <td>{item.itens.filter(equipamento => equipamento.status_item !== 'removido').length}</td>
                  <td><StatusBadge tone={status.tone}>{status.label}</StatusBadge></td>
                  <td>{formatDateTime(item.criado_em)}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" type="button" onClick={() => onDetails(item)}>Detalhes</button>
                    {(item.acoes_permitidas || []).includes('cancelar') && (
                      <button className="btn btn-danger btn-sm" type="button" onClick={() => onCancel(item)}>Cancelar</button>
                    )}
                    {(item.acoes_permitidas || []).includes('aceitar') && (
                      <button className="btn btn-primary btn-sm" type="button" onClick={() => onDetails(item)}>Ler e aceitar</button>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}
