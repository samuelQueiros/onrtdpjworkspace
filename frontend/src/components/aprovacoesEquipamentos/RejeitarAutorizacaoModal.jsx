import { useState } from 'react'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'

export default function RejeitarAutorizacaoModal({ autorizacao, onClose, onSubmit, saving }) {
  const [motivo, setMotivo] = useState('')

  const submit = event => {
    event.preventDefault()
    onSubmit({ motivo_rejeicao: motivo.trim() })
  }

  return (
    <ModalAutorizacaoBase
      busy={saving}
      className="autorizacao-action-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id} · ${autorizacao.user_nome}`}
      title="Rejeitar autorização"
      titleId="rejeitar-autorizacao-equipamento-title"
    >
      <form onSubmit={submit}>
        <div className="modal-body autorizacao-modal-body">
          <div className="alert alert-warning">A rejeição encerra esta solicitação. O colaborador poderá consultar o motivo informado.</div>
          <div className="form-group">
            <label htmlFor="rejeicao-autorizacao-motivo">Motivo da rejeição</label>
            <textarea
              id="rejeicao-autorizacao-motivo"
              data-autofocus
              value={motivo}
              onChange={event => setMotivo(event.target.value)}
              rows="4"
              minLength="3"
              maxLength="2000"
              required
              placeholder="Informe uma justificativa objetiva..."
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
          <button className="btn btn-danger" type="submit" disabled={saving || motivo.trim().length < 3}>{saving ? 'Rejeitando...' : 'Confirmar rejeição'}</button>
        </div>
      </form>
    </ModalAutorizacaoBase>
  )
}
