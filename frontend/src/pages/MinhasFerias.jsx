import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { EmptyState, LoadingCard, PageHeader, StatusBadge } from './_helpers'
import { formatDate } from '../utils/formatters'

const STATUS_TONE = { aprovada: 'green', pendente: 'amber', rejeitada: 'red' }
const STATUS_LABEL = { aprovada: 'Aprovada', pendente: 'Pendente', rejeitada: 'Rejeitada' }

function EditModal({ ferias, onClose, onSaved }) {
  const [dataInicio, setDataInicio] = useState(ferias.data_inicio)
  const [dataFim, setDataFim] = useState(ferias.data_fim)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const submit = async e => {
    e.preventDefault()
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
      <div className="modal" onClick={e => e.stopPropagation()}>
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
                <input type="date" value={dataInicio} onChange={e => setDataInicio(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Data de fim</label>
                <input type="date" value={dataFim} onChange={e => setDataFim(e.target.value)} required />
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

export default function MinhasFerias() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editando, setEditando] = useState(null)

  const load = () => api.minhasFerias().then(setData).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const ferias = data?.ferias || []
  const saldo = data?.saldo ?? user?.dias_restantes ?? 0

  const cancel = async id => {
    if (!confirm('Cancelar este período de férias?')) return
    setError('')
    try {
      await api.cancelarFerias(id)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Minhas Férias"
        subtitle="Histórico dos períodos registrados na sua conta."
        action={<Link className="btn btn-primary" to="/solicitar">Solicitar férias</Link>}
      />

      {error && <div className="alert alert-error spaced">{error}</div>}

      <section className="stat-grid stat-grid-3">
        <div className="stat-card">
          <div className="stat-label">Saldo disponível</div>
          <div className="stat-value">{saldo}</div>
          <div className="stat-sub">dias no ciclo atual</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Ciclo início</div>
          <div className="stat-value text-sm">{data?.ciclo_inicio ? formatDate(data.ciclo_inicio) : '—'}</div>
          <div className="stat-sub">início do período anual</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Ciclo fim</div>
          <div className="stat-value text-sm">{data?.ciclo_fim ? formatDate(data.ciclo_fim) : '—'}</div>
          <div className="stat-sub">encerramento do ciclo</div>
        </div>
      </section>

      <section className="card">
        <div className="table-wrap">
          {ferias.length ? (
            <table>
              <thead>
                <tr>
                  <th>Início</th>
                  <th>Fim</th>
                  <th>Dias</th>
                  <th>Tipo</th>
                  <th>Status</th>
                  <th>Motivo</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {ferias.map(item => (
                  <tr key={item.id}>
                    <td>{formatDate(item.data_inicio)}</td>
                    <td>{formatDate(item.data_fim)}</td>
                    <td>{item.dias_usados}</td>
                    <td>
                      {item.ferias_acordo
                        ? <StatusBadge tone="blue">Por acordo</StatusBadge>
                        : <StatusBadge tone="gray">Normal</StatusBadge>}
                    </td>
                    <td>
                      <StatusBadge tone={STATUS_TONE[item.status] || 'gray'}>
                        {STATUS_LABEL[item.status] || item.status}
                      </StatusBadge>
                    </td>
                    <td className="muted">{item.motivo_rejeicao || '—'}</td>
                    <td className="actions-cell">
                      {item.status === 'pendente' && (
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => setEditando(item)}
                        >
                          Editar
                        </button>
                      )}
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => cancel(item.id)}
                      >
                        Cancelar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title="Sem férias registradas"
              text="Solicite seu primeiro período para iniciar o controle."
            />
          )}
        </div>
      </section>

      {editando && (
        <EditModal
          ferias={editando}
          onClose={() => setEditando(null)}
          onSaved={() => { setEditando(null); load() }}
        />
      )}
    </>
  )
}
