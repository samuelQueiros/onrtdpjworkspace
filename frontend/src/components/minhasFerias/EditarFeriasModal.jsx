import { useState } from 'react'
import { api } from '../../services/api'

export default function EditarFeriasModal({ ferias, onClose, onSaved }) {
  const [dataInicio, setDataInicio] = useState(ferias.data_inicio)
  const [dataFim, setDataFim] = useState(ferias.data_fim)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const submit = async event => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.editarFerias(ferias.id, { data_inicio: dataInicio, data_fim: dataFim })
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={event => event.stopPropagation()}>
        <div className="modal-header">
          <h3>Editar solicitação</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={submit}>
          <div className="modal-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            <div className="form-row">
              <div className="form-group">
                <label>Data de início</label>
                <input type="date" value={dataInicio} onChange={event => setDataInicio(event.target.value)} required />
              </div>
              <div className="form-group">
                <label>Data de fim</label>
                <input type="date" value={dataFim} onChange={event => setDataFim(event.target.value)} required />
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button className="btn btn-outline" type="button" onClick={onClose}>Cancelar</button>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar alterações'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
