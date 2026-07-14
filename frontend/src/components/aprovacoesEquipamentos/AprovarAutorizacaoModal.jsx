import { useMemo, useState } from 'react'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'
import { descricaoItem, identificarItem } from './statusAutorizacoesEquipamentos'

export default function AprovarAutorizacaoModal({ autorizacao, onClose, onSubmit, saving }) {
  const items = useMemo(() => autorizacao.itens.filter(item => item.status_item !== 'removido'), [autorizacao])
  const [selected, setSelected] = useState(() => items.map(item => item.id))
  const [motivo, setMotivo] = useState('')
  const [permitirSegunda, setPermitirSegunda] = useState(false)
  const [justificativa, setJustificativa] = useState('')
  const [error, setError] = useState('')
  const parcial = selected.length < items.length
  const possuiMaquina = items.some(item => selected.includes(item.id) && ['notebook', 'desktop'].includes(item.tipo_snapshot))

  const toggle = id => {
    setSelected(current => current.includes(id) ? current.filter(itemId => itemId !== id) : [...current, id])
    setError('')
  }

  const submit = event => {
    event.preventDefault()
    if (!selected.length) return setError('Selecione ao menos um item para aprovação.')
    if (parcial && motivo.trim().length < 3) return setError('Informe o motivo da aprovação parcial.')
    if (permitirSegunda && justificativa.trim().length < 3) return setError('Justifique a autorização de uma segunda máquina principal.')
    onSubmit({
      item_ids_aprovados: selected,
      motivo_ajuste: parcial ? motivo.trim() : null,
      permitir_segunda_maquina: permitirSegunda,
      justificativa_excecao: permitirSegunda ? justificativa.trim() : null,
    })
  }

  return (
    <ModalAutorizacaoBase
      busy={saving}
      className="autorizacao-action-modal autorizacao-approval-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id} · ${autorizacao.user_nome}`}
      title="Aprovar autorização"
      titleId="aprovar-autorizacao-equipamento-title"
    >
      <form onSubmit={submit}>
        <div className="modal-body autorizacao-modal-body">
          <p className="muted-sm">Selecione os itens que serão aprovados. Itens desmarcados permanecerão no histórico como removidos.</p>
          <fieldset className="autorizacao-items-fieldset">
            <legend>Itens aprovados</legend>
            {items.map(item => (
              <label key={item.id} className={`autorizacao-select-item${selected.includes(item.id) ? ' is-selected' : ''}`}>
                <input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggle(item.id)} />
                <span><strong>{identificarItem(item)}</strong><small>{descricaoItem(item)} · {item.numero_serie_snapshot || 'sem série'}</small></span>
              </label>
            ))}
          </fieldset>

          {parcial && (
            <div className="form-group">
              <label htmlFor="aprovacao-parcial-motivo">Motivo da aprovação parcial</label>
              <textarea
                id="aprovacao-parcial-motivo"
                value={motivo}
                onChange={event => { setMotivo(event.target.value); setError('') }}
                rows="3"
                minLength="3"
                required
                placeholder="Explique por que os itens foram removidos..."
              />
            </div>
          )}

          {possuiMaquina && autorizacao.tipo_solicitacao === 'item_diferente' && (
            <>
              <label className="autorizacao-option-card">
                <input type="checkbox" checked={permitirSegunda} onChange={event => setPermitirSegunda(event.target.checked)} />
                <span><strong>Permitir segunda máquina principal</strong><small>Use apenas quando o colaborador puder manter outra máquina ativa.</small></span>
              </label>
              {permitirSegunda && (
                <div className="form-group">
                  <label htmlFor="aprovacao-excecao-justificativa">Justificativa da exceção</label>
                  <textarea id="aprovacao-excecao-justificativa" value={justificativa} onChange={event => setJustificativa(event.target.value)} rows="3" minLength="3" required />
                </div>
              )}
            </>
          )}

          {error && <div className="alert alert-error" role="alert">{error}</div>}
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
          <button className="btn btn-primary" type="submit" disabled={saving}>{saving ? 'Aprovando...' : parcial ? 'Aprovar parcialmente' : 'Aprovar solicitação'}</button>
        </div>
      </form>
    </ModalAutorizacaoBase>
  )
}
