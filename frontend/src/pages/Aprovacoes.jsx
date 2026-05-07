import { useEffect, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

function RejeitarModal({ ferias, onClose, onRejeitado }) {
  const [motivo, setMotivo] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const submit = async e => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.rejeitarFerias(ferias.id, motivo)
      onRejeitado()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Rejeitar solicitação</h3>
          <button className="btn-close" onClick={onClose}>×</button>
        </div>
        <form onSubmit={submit}>
          <div className="modal-body form-stack">
            <p>
              Rejeitar férias de <strong>{ferias.nome_usuario}</strong> —{' '}
              {formatDate(ferias.data_inicio)} a {formatDate(ferias.data_fim)} ({ferias.dias_usados} dias)
            </p>
            {error && <div className="alert alert-error">{error}</div>}
            <div className="form-group">
              <label>Motivo da rejeição (opcional)</label>
              <textarea
                value={motivo}
                onChange={e => setMotivo(e.target.value)}
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

export default function Aprovacoes() {
  const [pendentes, setPendentes] = useState([])
  const [loading, setLoading] = useState(true)
  const [rejeitando, setRejeitando] = useState(null)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  const load = () => api.feriasPendentes().then(setPendentes).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const aprovar = async id => {
    setMsg('')
    setError('')
    try {
      await api.aprovarFerias(id)
      setMsg('Férias aprovadas com sucesso.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Aprovação de Férias"
        subtitle="Revise e aprove ou rejeite as solicitações pendentes."
      />

      {msg && <div className="alert alert-success spaced">{msg}</div>}
      {error && <div className="alert alert-error spaced">{error}</div>}

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Solicitações pendentes</h2>
          <StatusBadge tone={pendentes.length > 0 ? 'amber' : 'gray'}>{pendentes.length} pendente(s)</StatusBadge>
        </div>
        <div className="table-wrap">
          {pendentes.length ? (
            <table>
              <thead>
                <tr>
                  <th>Colaborador</th>
                  <th>Início</th>
                  <th>Fim</th>
                  <th>Dias</th>
                  <th>Tipo</th>
                  <th>Solicitado em</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {pendentes.map(item => (
                  <tr key={item.id}>
                    <td><strong>{item.nome_usuario}</strong></td>
                    <td>{formatDate(item.data_inicio)}</td>
                    <td>{formatDate(item.data_fim)}</td>
                    <td>{item.dias_usados}</td>
                    <td>
                      {item.ferias_acordo
                        ? <StatusBadge tone="blue">Por acordo</StatusBadge>
                        : <StatusBadge tone="gray">Normal</StatusBadge>}
                    </td>
                    <td>{formatDate(item.criado_em)}</td>
                    <td className="actions-cell">
                      <button className="btn btn-primary btn-sm" onClick={() => aprovar(item.id)}>
                        Aprovar
                      </button>
                      <button className="btn btn-danger btn-sm" onClick={() => setRejeitando(item)}>
                        Rejeitar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="Nenhuma solicitação pendente"
              text="Quando colaboradores enviarem férias, elas aparecerão aqui para aprovação."
            />
          )}
        </div>
      </section>

      {rejeitando && (
        <RejeitarModal
          ferias={rejeitando}
          onClose={() => setRejeitando(null)}
          onRejeitado={() => { setRejeitando(null); setMsg('Férias rejeitadas.'); load() }}
        />
      )}
    </>
  )
}
