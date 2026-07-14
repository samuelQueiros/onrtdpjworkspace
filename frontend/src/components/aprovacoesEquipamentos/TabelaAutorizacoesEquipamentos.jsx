import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { STATUS_AUTORIZACAO, STATUS_DOCUMENTO, formatarDataHoraSaoPaulo } from './statusAutorizacoesEquipamentos'

const ACTIONS = {
  aprovar: { label: 'Analisar', className: 'btn-primary' },
  rejeitar: { label: 'Rejeitar', className: 'btn-danger' },
  registrar_entrega: { label: 'Registrar entrega', className: 'btn-navy' },
  registrar_devolucao: { label: 'Registrar devolução', className: 'btn-outline' },
  regenerar_documento: { label: 'Gerar termo novamente', className: 'btn-outline' },
  cancelar: { label: 'Cancelar', className: 'btn-danger' },
}

export default function TabelaAutorizacoesEquipamentos({ items, loading, mutatingId, onAction, onDetails }) {
  return (
    <section className="card" aria-busy={loading}>
      <div className="card-header autorizacao-list-header">
        <div>
          <h2 className="card-title">Autorizações de equipamentos</h2>
          <p className="muted-xs mt-4">Aprovação, entrega, aceite e devolução são etapas independentes.</p>
        </div>
        <div className="inline-center gap-8">
          {loading && <span className="spinner" aria-label="Atualizando solicitações" />}
          <StatusBadge tone={items.some(item => item.status === 'pendente') ? 'amber' : 'gray'}>
            {items.length} registro(s)
          </StatusBadge>
        </div>
      </div>

      <div className="table-wrap">
        {items.length ? (
          <table className="autorizacoes-equipamentos-table">
            <caption className="sr-only">Solicitações administrativas de autorização de equipamentos</caption>
            <thead>
              <tr>
                <th>Solicitação</th>
                <th>Colaborador</th>
                <th>Itens</th>
                <th>Status</th>
                <th>Termo</th>
                <th>Solicitado em</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => {
                const status = STATUS_AUTORIZACAO[item.status] || { label: item.status, tone: 'gray' }
                const documento = STATUS_DOCUMENTO[item.documento_status] || { label: item.documento_status, tone: 'gray' }
                const activeItems = item.itens.filter(equipamento => equipamento.status_item !== 'removido')
                const actions = (item.acoes_permitidas || []).filter(action => ACTIONS[action])
                const busy = mutatingId === item.id
                return (
                  <tr key={item.id}>
                    <td><strong>#{item.id}</strong><span className="autorizacao-table-sub">{item.tipo_solicitacao === 'item_diferente' ? 'Item diferente' : 'Itens vinculados'}</span></td>
                    <td><strong>{item.user_nome}</strong><span className="autorizacao-table-sub">{item.user_cpf_mascarado || 'CPF não informado'}</span></td>
                    <td>{activeItems.length} item(ns)</td>
                    <td><StatusBadge tone={status.tone}>{status.label}</StatusBadge></td>
                    <td><StatusBadge tone={documento.tone}>{documento.label}</StatusBadge></td>
                    <td>{formatarDataHoraSaoPaulo(item.criado_em)}</td>
                    <td className="actions-cell">
                      <button className="btn btn-outline btn-sm" type="button" onClick={() => onDetails(item)}>Detalhes</button>
                      {actions.map(action => (
                        <button
                          key={action}
                          className={`btn ${ACTIONS[action].className} btn-sm`}
                          type="button"
                          disabled={busy}
                          onClick={() => onAction(action, item)}
                        >
                          {busy ? 'Processando...' : ACTIONS[action].label}
                        </button>
                      ))}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        ) : !loading ? (
          <EmptyState
            title="Nenhuma autorização encontrada"
            text="Altere os filtros ou aguarde o envio de uma nova solicitação de equipamento."
          />
        ) : null}
      </div>
    </section>
  )
}
