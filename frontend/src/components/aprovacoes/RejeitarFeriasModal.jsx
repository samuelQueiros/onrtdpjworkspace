import { useState } from 'react'
import { useToast } from '../../contexts/ToastContext'
import { api } from '../../services/api'
import { formatDate } from '../../utils/formatters'

export default function RejeitarFeriasModal({ ferias, onClose, onRejeitado }) {
  const toast = useToast()
  const [motivo, setMotivo] = useState('')
  const [saving, setSaving] = useState(false)

  const submit = async event => {
    event.preventDefault()
    setSaving(true)
    try {
      await api.rejeitarFerias(ferias.id, motivo)
      onRejeitado()
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={event => event.stopPropagation()}>
        <div className="modal-header">
          <h3>Rejeitar solicitação</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={submit}>
          <div className="modal-body form-stack">
            <p>
              Rejeitar férias de <strong>{ferias.nome_usuario}</strong> -{' '}
              {formatDate(ferias.data_inicio)} a {formatDate(ferias.data_fim)} ({ferias.dias_usados} dias)
            </p>
            <div className="form-group">
              <label>Motivo da rejeição (opcional)</label>
              <textarea
                value={motivo}
                onChange={event => setMotivo(event.target.value)}
                rows={3}
                placeholder="Informe o motivo para o colaborador..."
              />
            </div>
          </div>
          <div className="modal-footer">
            <button className="btn btn-outline" type="button" onClick={onClose}>Cancelar</button>
            <button className="btn btn-danger" type="submit" disabled={saving}>
              {saving ? 'Rejeitando...' : 'Confirmar rejeição'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
