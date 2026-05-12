import { useEffect, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

const blank = { data_inicio: '', data_fim: '', motivo: '', tipo: 'bloqueio' }

export default function Bloqueios() {
  const [bloqueios, setBloqueios] = useState([])
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [filtro, setFiltro] = useState('todos')

  const load = () =>
    api.listarBloqueios()
      .then(setBloqueios)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const save = async e => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      if (editing) {
        await api.editarBloqueio(editing, form)
        setSuccess('Período atualizado com sucesso.')
      } else {
        await api.criarBloqueio(form)
        setSuccess('Período cadastrado com sucesso.')
      }
      setForm(blank)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const startEdit = b => {
    setEditing(b.id)
    setForm({
      data_inicio: b.data_inicio,
      data_fim: b.data_fim,
      motivo: b.motivo,
      tipo: b.tipo,
    })
    setError('')
    setSuccess('')
  }

  const excluir = async id => {
    if (!confirm('Excluir este bloqueio/recesso?')) return
    setError('')
    try {
      await api.excluirBloqueio(id)
      setSuccess('Período excluído.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const filtrados = bloqueios.filter(b =>
    filtro === 'todos' ? true : b.tipo === filtro
  )

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Bloqueio de Datas"
        subtitle="Impeça marcação de férias em períodos específicos como auditorias, fechamentos e recessos."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">Períodos cadastrados</h2>
            <div style={{ display: 'flex', gap: 8 }}>
              {['todos', 'bloqueio', 'recesso'].map(t => (
                <button
                  key={t}
                  className={`filter-tab sm${filtro === t ? ' active' : ''}`}
                  onClick={() => setFiltro(t)}
                >
                  {t === 'todos' ? 'Todos' : t === 'bloqueio' ? 'Bloqueios' : 'Recessos'}
                  <span className="filter-tab-count">
                    {t === 'todos' ? bloqueios.length : bloqueios.filter(b => b.tipo === t).length}
                  </span>
                </button>
              ))}
            </div>
          </div>
          <div className="table-wrap">
            {filtrados.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Motivo</th>
                    <th>Criado por</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtrados.map(b => (
                    <tr key={b.id}>
                      <td>
                        <StatusBadge tone={b.tipo === 'recesso' ? 'blue' : 'red'}>
                          {b.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                        </StatusBadge>
                      </td>
                      <td>{formatDate(b.data_inicio)}</td>
                      <td>{formatDate(b.data_fim)}</td>
                      <td><strong>{b.motivo}</strong></td>
                      <td>{b.criado_por_nome || <span className="muted">—</span>}</td>
                      <td className="actions-cell">
                        <button className="btn btn-outline btn-sm" onClick={() => startEdit(b)}>
                          Editar
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => excluir(b.id)}>
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="Nenhum período cadastrado"
                text="Cadastre bloqueios para impedir marcação de férias em datas críticas."
              />
            )}
          </div>
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header">
            <h2 className="card-title">{editing ? 'Editar período' : 'Novo período'}</h2>
          </div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="form-group">
              <label>Tipo</label>
              <select value={form.tipo} onChange={e => setForm({ ...form, tipo: e.target.value })}>
                <option value="bloqueio">Bloqueio — impede novas solicitações</option>
                <option value="recesso">Recesso — período coletivo de folga</option>
              </select>
            </div>

            <div className="form-group">
              <label>Motivo / Descrição</label>
              <input
                type="text"
                value={form.motivo}
                onChange={e => setForm({ ...form, motivo: e.target.value })}
                placeholder="Ex.: Auditoria interna, Recesso de Natal..."
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Data início</label>
                <input
                  type="date"
                  value={form.data_inicio}
                  onChange={e => setForm({ ...form, data_inicio: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Data fim</label>
                <input
                  type="date"
                  value={form.data_fim}
                  onChange={e => setForm({ ...form, data_fim: e.target.value })}
                  required
                />
              </div>
            </div>

            {form.tipo === 'bloqueio' && (
              <div className="alert alert-info">
                <p>Colaboradores <strong>não poderão</strong> solicitar férias neste período. Uma mensagem amigável será exibida ao tentar.</p>
              </div>
            )}
            {form.tipo === 'recesso' && (
              <div className="alert alert-info">
                O recesso aparece destacado no calendário. Colaboradores verão o período como recesso coletivo.
              </div>
            )}

            <div className="button-row">
              {editing && (
                <button
                  className="btn btn-outline"
                  type="button"
                  onClick={() => { setEditing(null); setForm(blank); setError(''); setSuccess('') }}
                >
                  Cancelar
                </button>
              )}
              <button className="btn btn-primary" type="submit">
                {editing ? 'Salvar alterações' : 'Cadastrar período'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}
