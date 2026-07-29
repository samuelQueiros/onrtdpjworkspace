import { useState } from 'react'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'

export default function CancelarAutorizacaoModal({ autorizacao, onClose, onSubmit, saving }) {
  const [motivo, setMotivo] = useState('')

  const submit = event => {
    event.preventDefault()
    onSubmit({ motivo: motivo.trim() })
  }

  return (
    <ModalAutorizacaoBase
      busy={saving}
      className="autorizacao-action-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id} · ${autorizacao.user_nome}`}
      title="Cancelar autorização antes da entrega"
      titleId="cancelar-autorizacao-equipamento-title"
    >
      <form onSubmit={submit}>
        <div className="modal-body autorizacao-modal-body">
          <div className="alert alert-warning" role="alert">
            O cancelamento libera os equipamentos reservados e encerra o fluxo antes da entrega.
          </div>
          <div className="form-group">
            <label htmlFor="cancelamento-autorizacao-motivo">Motivo do cancelamento</label>
            <textarea
              id="cancelamento-autorizacao-motivo"
              name="motivo"
              data-autofocus
              value={motivo}
              onChange={event => setMotivo(event.target.value)}
              rows="4"
              minLength="3"
              maxLength="1000"
              required
              placeholder="Informe por que a entrega não será realizada..."
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Voltar</button>
          <button className="btn btn-danger" type="submit" disabled={saving || motivo.trim().length < 3}>
            {saving ? 'Cancelando...' : 'Confirmar cancelamento'}
          </button>
        </div>
      </form>
    </ModalAutorizacaoBase>
  )
}
