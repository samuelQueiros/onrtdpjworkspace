import { useMemo, useState } from 'react'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'
import { descricaoItem, identificarItem } from './statusAutorizacoesEquipamentos'

export default function EntregaAutorizacaoModal({ autorizacao, onClose, onSubmit, saving }) {
  const items = useMemo(() => autorizacao.itens.filter(item => item.status_item === 'aprovado'), [autorizacao])
  const [responsavelNome, setResponsavelNome] = useState('')
  const [responsavelCargo, setResponsavelCargo] = useState('')
  const [local, setLocal] = useState('')
  const [permitirSegunda, setPermitirSegunda] = useState(false)
  const [justificativa, setJustificativa] = useState('')
  const [itemValues, setItemValues] = useState(() => Object.fromEntries(items.map(item => [item.id, {
    estado_conservacao: item.estado_conservacao_snapshot || '',
    observacoes: item.observacoes_snapshot || '',
  }])))
  const possuiMaquinaDiferente = autorizacao.tipo_solicitacao === 'item_diferente'
    && items.some(item => ['notebook', 'desktop'].includes(item.tipo_snapshot))

  const updateItem = (id, field, value) => setItemValues(current => ({
    ...current,
    [id]: { ...current[id], [field]: value },
  }))

  const submit = event => {
    event.preventDefault()
    onSubmit({
      responsavel_entrega_nome: responsavelNome.trim(),
      responsavel_entrega_cargo: responsavelCargo.trim(),
      local_entrega: local.trim(),
      itens: items.map(item => ({
        item_id: item.id,
        estado_conservacao: itemValues[item.id].estado_conservacao.trim(),
        observacoes: itemValues[item.id].observacoes.trim() || null,
      })),
      permitir_segunda_maquina: permitirSegunda,
      justificativa_excecao: permitirSegunda ? justificativa.trim() : null,
    })
  }

  return (
    <ModalAutorizacaoBase
      busy={saving}
      className="autorizacao-action-modal autorizacao-delivery-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id} · ${autorizacao.user_nome}`}
      title="Registrar entrega"
      titleId="entrega-autorizacao-equipamento-title"
    >
      <form onSubmit={submit}>
        <div className="modal-body autorizacao-modal-body">
          <div className="alert alert-info">A entrega será registrada separadamente do aceite do colaborador. Data e hora serão definidas pelo sistema.</div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="entrega-responsavel-nome">Responsável pela entrega</label>
              <input id="entrega-responsavel-nome" data-autofocus value={responsavelNome} onChange={event => setResponsavelNome(event.target.value)} minLength="2" maxLength="150" required />
            </div>
            <div className="form-group">
              <label htmlFor="entrega-responsavel-cargo">Cargo do responsável</label>
              <input id="entrega-responsavel-cargo" value={responsavelCargo} onChange={event => setResponsavelCargo(event.target.value)} minLength="2" maxLength="120" required />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="entrega-local">Local da entrega</label>
            <input id="entrega-local" value={local} onChange={event => setLocal(event.target.value)} minLength="2" maxLength="180" required placeholder="Ex.: Sede administrativa" />
          </div>

          <fieldset className="autorizacao-items-fieldset">
            <legend>Condição dos itens entregues</legend>
            {items.map(item => (
              <article key={item.id} className="autorizacao-delivery-item">
                <div><strong>{identificarItem(item)}</strong><small>{descricaoItem(item)}</small></div>
                <div className="form-group">
                  <label htmlFor={`entrega-estado-${item.id}`}>Estado de conservação</label>
                  <input id={`entrega-estado-${item.id}`} value={itemValues[item.id].estado_conservacao} onChange={event => updateItem(item.id, 'estado_conservacao', event.target.value)} minLength="2" maxLength="300" required />
                </div>
                <div className="form-group">
                  <label htmlFor={`entrega-observacoes-${item.id}`}>Observações</label>
                  <textarea id={`entrega-observacoes-${item.id}`} value={itemValues[item.id].observacoes} onChange={event => updateItem(item.id, 'observacoes', event.target.value)} rows="2" maxLength="1000" />
                </div>
              </article>
            ))}
          </fieldset>

          {possuiMaquinaDiferente && (
            <>
              <label className="autorizacao-option-card">
                <input type="checkbox" checked={permitirSegunda} onChange={event => setPermitirSegunda(event.target.checked)} />
                <span><strong>Confirmar exceção de segunda máquina</strong><small>Necessário caso o colaborador já possua notebook ou desktop ativo.</small></span>
              </label>
              {permitirSegunda && (
                <div className="form-group">
                  <label htmlFor="entrega-excecao-justificativa">Justificativa da exceção</label>
                  <textarea id="entrega-excecao-justificativa" value={justificativa} onChange={event => setJustificativa(event.target.value)} minLength="3" rows="3" required />
                </div>
              )}
            </>
          )}
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
          <button className="btn btn-navy" type="submit" disabled={saving || !items.length}>{saving ? 'Registrando...' : 'Confirmar entrega'}</button>
        </div>
      </form>
    </ModalAutorizacaoBase>
  )
}
