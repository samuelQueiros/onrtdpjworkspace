import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { LoadingCard, PageHeader, StatusBadge } from './_helpers'

const blank = { nome: '', limite_simultaneo: 2 }

export default function Departamentos() {
  const [deps, setDeps] = useState([])
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () => api.listarDepartamentos().then(setDeps).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const save = async e => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      const payload = { nome: form.nome, limite_simultaneo: Number(form.limite_simultaneo) }
      if (editing) {
        await api.editarDepartamento(editing, payload)
        setSuccess('Departamento atualizado.')
      } else {
        await api.criarDepartamento(payload)
        setSuccess('Departamento criado.')
      }
      setForm(blank)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const excluir = async id => {
    if (!confirm('Excluir este departamento? Os usuários vinculados ficarão sem setor.')) return
    setError('')
    try {
      await api.excluirDepartamento(id)
      setSuccess('Departamento excluído.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const startEdit = dep => {
    setEditing(dep.id)
    setForm({ nome: dep.nome, limite_simultaneo: dep.limite_simultaneo })
    setError('')
    setSuccess('')
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Departamentos"
        subtitle="Gerencie setores e configure limites de férias simultâneas."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Setores cadastrados</h2></div>
          <div className="table-wrap">
            {deps.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Limite simultâneo</th>
                    <th>Usuários</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {deps.map(dep => (
                    <tr key={dep.id}>
                      <td><strong>{dep.nome}</strong></td>
                      <td>
                        <StatusBadge tone="navy">{dep.limite_simultaneo} simultâneo(s)</StatusBadge>
                      </td>
                      <td>{dep.total_usuarios}</td>
                      <td className="actions-cell">
                        <button className="btn btn-outline btn-sm" onClick={() => startEdit(dep)}>Editar</button>
                        <button className="btn btn-danger btn-sm" onClick={() => excluir(dep.id)}>Excluir</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty">
                <p>Nenhum departamento cadastrado.</p>
              </div>
            )}
          </div>
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header">
            <h2 className="card-title">{editing ? 'Editar departamento' : 'Novo departamento'}</h2>
          </div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="form-group">
              <label>Nome do setor</label>
              <input
                value={form.nome}
                onChange={e => setForm({ ...form, nome: e.target.value })}
                placeholder="Ex: Tecnologia da Informação"
                required
              />
            </div>
            <div className="form-group">
              <label>Limite de férias simultâneas</label>
              <input
                type="number"
                min="1"
                max="50"
                value={form.limite_simultaneo}
                onChange={e => setForm({ ...form, limite_simultaneo: e.target.value })}
                required
              />
              <small className="form-hint">
                Máximo de colaboradores do setor em férias ao mesmo tempo.
              </small>
            </div>

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
                {editing ? 'Salvar alterações' : 'Criar departamento'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}
