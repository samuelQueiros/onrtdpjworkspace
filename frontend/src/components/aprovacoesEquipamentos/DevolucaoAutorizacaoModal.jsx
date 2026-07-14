import { useMemo, useState } from 'react'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'
import { descricaoItem, identificarItem } from './statusAutorizacoesEquipamentos'

export default function DevolucaoAutorizacaoModal({ autorizacao, onClose, onSubmit, saving }) {
  const items = useMemo(() => autorizacao.itens.filter(item => item.status_item === 'entregue'), [autorizacao])
  const [estadoGeral, setEstadoGeral] = useState('')
  const [observacoes, setObservacoes] = useState('')
  const [itemValues, setItemValues] = useState(() => Object.fromEntries(items.map(item => [item.id, {
    situacao: 'devolvido',
    estado_conservacao: item.estado_conservacao_snapshot || '',
    observacoes: '',
  }])))

  const updateItem = (id, field, value) => setItemValues(current => ({
    ...current,
    [id]: { ...current[id], [field]: value },
  }))

  const submit = event => {
    event.preventDefault()
    onSubmit({
      itens: items.map(item => ({
        item_id: item.id,
        situacao: itemValues[item.id].situacao,
        estado_conservacao: itemValues[item.id].situacao === 'devolvido'
          ? itemValues[item.id].estado_conservacao.trim()
          : null,
        observacoes: itemValues[item.id].observacoes.trim() || null,
      })),
      estado_conservacao_geral: estadoGeral.trim(),
      observacoes: observacoes.trim() || null,
    })
  }

  return (
    <ModalAutorizacaoBase
      busy={saving}
      className="autorizacao-action-modal autorizacao-return-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id} · ${autorizacao.user_nome}`}
      title="Registrar devolução"
      titleId="devolucao-autorizacao-equipamento-title"
    >
      <form onSubmit={submit}>
        <div className="modal-body autorizacao-modal-body">
          <div className="alert alert-warning">Confira todos os itens. Equipamentos ausentes permanecerão explicitamente registrados no histórico.</div>
          <fieldset className="autorizacao-items-fieldset">
            <legend>Situação dos itens</legend>
            {items.map(item => {
              const values = itemValues[item.id]
              return (
                <article key={item.id} className={`autorizacao-delivery-item${values.situacao === 'ausente' ? ' is-missing' : ''}`}>
                  <div><strong>{identificarItem(item)}</strong><small>{descricaoItem(item)}</small></div>
                  <div className="form-row">
                    <div className="form-group">
                      <label htmlFor={`devolucao-situacao-${item.id}`}>Situação</label>
                      <select id={`devolucao-situacao-${item.id}`} value={values.situacao} onChange={event => updateItem(item.id, 'situacao', event.target.value)}>
                        <option value="devolvido">Devolvido</option>
                        <option value="ausente">Ausente</option>
                      </select>
                    </div>
                    {values.situacao === 'devolvido' && (
                      <div className="form-group">
                        <label htmlFor={`devolucao-estado-${item.id}`}>Estado de conservação</label>
                        <input id={`devolucao-estado-${item.id}`} value={values.estado_conservacao} onChange={event => updateItem(item.id, 'estado_conservacao', event.target.value)} minLength="2" maxLength="300" required />
                      </div>
                    )}
                  </div>
                  <div className="form-group">
                    <label htmlFor={`devolucao-observacoes-${item.id}`}>Observações do item</label>
                    <textarea id={`devolucao-observacoes-${item.id}`} value={values.observacoes} onChange={event => updateItem(item.id, 'observacoes', event.target.value)} rows="2" maxLength="1000" placeholder={values.situacao === 'ausente' ? 'Informe o ocorrido...' : 'Opcional'} />
                  </div>
                </article>
              )
            })}
          </fieldset>

          <div className="form-group">
            <label htmlFor="devolucao-estado-geral">Estado geral da devolução</label>
            <input id="devolucao-estado-geral" data-autofocus value={estadoGeral} onChange={event => setEstadoGeral(event.target.value)} minLength="2" maxLength="300" required placeholder="Ex.: Itens conferidos e em bom estado" />
          </div>
          <div className="form-group">
            <label htmlFor="devolucao-observacoes-gerais">Observações gerais</label>
            <textarea id="devolucao-observacoes-gerais" value={observacoes} onChange={event => setObservacoes(event.target.value)} rows="3" maxLength="2000" />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
          <button className="btn btn-navy" type="submit" disabled={saving || !items.length}>{saving ? 'Registrando...' : 'Confirmar devolução'}</button>
        </div>
      </form>
    </ModalAutorizacaoBase>
  )
}
