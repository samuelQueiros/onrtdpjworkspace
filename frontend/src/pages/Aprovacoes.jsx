import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge } from './_helpers'
import { formatDate, formatDateTime } from '../utils/formatters'

const STATUS_LABELS = {
  pendente: { label: 'Pendente', tone: 'amber' },
  aprovada: { label: 'Aprovada', tone: 'green' },
  rejeitada: { label: 'Rejeitada', tone: 'red' },
}

function UserDot({ cor, nome }) {
  const bg = cor || '#64748b'
  return (
    <span
      style={{
        display: 'inline-block',
        width: 10,
        height: 10,
        borderRadius: '50%',
        background: bg,
        marginRight: 6,
        flexShrink: 0,
        verticalAlign: 'middle',
      }}
      title={nome}
    />
  )
}

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
  const [todas, setTodas] = useState([])
  const [loading, setLoading] = useState(true)
  const [rejeitando, setRejeitando] = useState(null)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [filtro, setFiltro] = useState('pendente')

  const load = () =>
    api.todasFerias()
      .then(setTodas)
      .finally(() => setLoading(false))

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

  const filtradas = todas.filter(f =>
    filtro === 'todas' ? true : f.status === filtro
  )

  const counts = {
    pendente: todas.filter(f => f.status === 'pendente').length,
    aprovada: todas.filter(f => f.status === 'aprovada').length,
    rejeitada: todas.filter(f => f.status === 'rejeitada').length,
    todas: todas.length,
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Aprovação de Férias"
        subtitle="Gerencie todas as solicitações de férias — pendentes, aprovadas e rejeitadas."
      />

      {msg && <div className="alert alert-success spaced">{msg}</div>}
      {error && <div className="alert alert-error spaced">{error}</div>}

      {/* Filtros */}
      <div className="filter-tabs spaced">
        {[
          { key: 'pendente', label: 'Pendentes', count: counts.pendente },
          { key: 'aprovada', label: 'Aprovadas', count: counts.aprovada },
          { key: 'rejeitada', label: 'Rejeitadas', count: counts.rejeitada },
          { key: 'todas', label: 'Todas', count: counts.todas },
        ].map(tab => (
          <button
            key={tab.key}
            className={`filter-tab${filtro === tab.key ? ' active' : ''}`}
            onClick={() => setFiltro(tab.key)}
          >
            {tab.label}
            <span className="filter-tab-count">{tab.count}</span>
          </button>
        ))}
      </div>

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">
            {filtro === 'todas' ? 'Todas as solicitações' :
             filtro === 'pendente' ? 'Solicitações pendentes' :
             filtro === 'aprovada' ? 'Férias aprovadas' : 'Férias rejeitadas'}
          </h2>
          <StatusBadge tone={filtro === 'pendente' && filtradas.length > 0 ? 'amber' : 'gray'}>
            {filtradas.length} registro(s)
          </StatusBadge>
        </div>
        <div className="table-wrap">
          {filtradas.length ? (
            <table>
              <thead>
                <tr>
                  <th>Colaborador</th>
                  <th>Início</th>
                  <th>Fim</th>
                  <th>Dias</th>
                  <th>Tipo</th>
                  <th>Status</th>
                  <th>Solicitado em</th>
                  <th>Histórico</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filtradas.map(item => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <UserDot cor={item.cor_usuario} nome={item.nome_usuario} />
                        <strong>{item.nome_usuario}</strong>
                      </div>
                    </td>
                    <td>{formatDate(item.data_inicio)}</td>
                    <td>{formatDate(item.data_fim)}</td>
                    <td>{item.dias_usados}</td>
                    <td>
                      {item.ferias_acordo
                        ? <StatusBadge tone="blue">Por acordo</StatusBadge>
                        : <StatusBadge tone="gray">Normal</StatusBadge>}
                    </td>
                    <td>
                      <StatusBadge tone={STATUS_LABELS[item.status]?.tone || 'gray'}>
                        {STATUS_LABELS[item.status]?.label || item.status}
                      </StatusBadge>
                    </td>
                    <td>{formatDate(item.criado_em)}</td>
                    <td>
                      {item.status === 'aprovada' && item.aprovado_por_nome && (
                        <span className="historico-info green">
                          ✓ {item.aprovado_por_nome}
                          <br />
                          <small>{formatDateTime(item.aprovado_em)}</small>
                        </span>
                      )}
                      {item.status === 'rejeitada' && item.rejeitado_por_nome && (
                        <span className="historico-info red">
                          ✗ {item.rejeitado_por_nome}
                          <br />
                          <small>{formatDateTime(item.rejeitado_em)}</small>
                          {item.motivo_rejeicao && (
                            <><br /><em>"{item.motivo_rejeicao}"</em></>
                          )}
                        </span>
                      )}
                      {item.status === 'pendente' && (
                        <span className="muted">Aguardando</span>
                      )}
                    </td>
                    <td className="actions-cell">
                      {item.status === 'pendente' ? (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => aprovar(item.id)}>
                            Aprovar
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={() => setRejeitando(item)}>
                            Rejeitar
                          </button>
                        </>
                      ) : (
                        <span className="muted" style={{ fontSize: 12 }}>—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState
              title={
                filtro === 'pendente' ? 'Nenhuma solicitação pendente' :
                filtro === 'aprovada' ? 'Nenhuma féria aprovada' :
                filtro === 'rejeitada' ? 'Nenhuma féria rejeitada' :
                'Nenhum registro encontrado'
              }
              text={
                filtro === 'pendente'
                  ? 'Quando colaboradores enviarem solicitações, elas aparecerão aqui.'
                  : 'Utilize os filtros para visualizar outros status.'
              }
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
