import { useEffect, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'
import { useAuth } from '../context/AuthContext'

const blank = { nome: '', email: '', senha: '', role: 'user', dias_totais: 30, departamento_id: '', data_admissao: '' }

export default function Usuarios() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () =>
    Promise.all([api.listarUsuarios(), api.listarDepartamentos()])
      .then(([u, d]) => { setUsers(u); setDepartamentos(d) })
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const save = async event => {
    event.preventDefault()
    setError('')
    setSuccess('')
    try {
      const payload = {
        nome: form.nome,
        email: form.email,
        dias_totais: Number(form.dias_totais),
        departamento_id: form.departamento_id ? Number(form.departamento_id) : null,
        data_admissao: form.data_admissao || null,
      }
      if (editing) {
        if (form.senha) payload.senha = form.senha
        await api.editarUsuario(editing, payload)
        setSuccess('Usuário atualizado com sucesso.')
      } else {
        payload.senha = form.senha
        payload.role = form.role
        await api.criarUsuario(payload)
        setSuccess('Usuário criado com sucesso.')
      }
      setForm(blank)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const startEdit = user => {
    setEditing(user.id)
    setForm({
      nome: user.nome,
      email: user.email,
      senha: '',
      role: user.role,
      dias_totais: user.dias_totais,
      departamento_id: user.departamento_id || '',
      data_admissao: user.data_admissao || '',
    })
    setError('')
    setSuccess('')
  }

  const excluir = async id => {
    if (!confirm('Excluir este usuário? Todas as férias associadas também serão removidas.')) return
    setError('')
    try {
      await api.excluirUsuario(id)
      setSuccess('Usuário excluído.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader title="Usuários" subtitle="Cadastre colaboradores e ajuste saldos anuais de férias." />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Colaboradores ({users.length})</h2></div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nome</th>
                  <th>E-mail</th>
                  <th>Perfil</th>
                  <th>Departamento</th>
                  <th>Saldo</th>
                  <th>Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.nome}</td>
                    <td>{user.email}</td>
                    <td>
                      <StatusBadge tone={user.role === 'admin' ? 'navy' : 'gray'}>
                        {user.role === 'admin' ? 'Admin' : 'Usuário'}
                      </StatusBadge>
                    </td>
                    <td>{user.departamento?.nome || <span className="muted">—</span>}</td>
                    <td>{user.dias_restantes}</td>
                    <td>{user.dias_totais}</td>
                    <td className="actions-cell">
                      <button className="btn btn-outline btn-sm" onClick={() => startEdit(user)}>
                        Editar
                      </button>
                      {user.id !== currentUser?.id && (
                        <button className="btn btn-danger btn-sm" onClick={() => excluir(user.id)}>
                          Excluir
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header">
            <h2 className="card-title">{editing ? 'Editar usuário' : 'Novo usuário'}</h2>
          </div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="form-group">
              <label>Nome</label>
              <input
                value={form.nome}
                onChange={e => setForm({ ...form, nome: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>E-mail</label>
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>{editing ? 'Nova senha (deixe em branco para manter)' : 'Senha'}</label>
              <input
                type="password"
                value={form.senha}
                onChange={e => setForm({ ...form, senha: e.target.value })}
                required={!editing}
              />
            </div>
            {!editing && (
              <div className="form-group">
                <label>Perfil</label>
                <select value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
                  <option value="user">Usuário</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
            )}
            <div className="form-group">
              <label>Departamento</label>
              <select
                value={form.departamento_id}
                onChange={e => setForm({ ...form, departamento_id: e.target.value })}
              >
                <option value="">Sem departamento</option>
                {departamentos.map(d => (
                  <option key={d.id} value={d.id}>{d.nome}</option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Dias totais</label>
                <input
                  type="number"
                  min="0"
                  value={form.dias_totais}
                  onChange={e => setForm({ ...form, dias_totais: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Data de admissão</label>
                <input
                  type="date"
                  value={form.data_admissao}
                  onChange={e => setForm({ ...form, data_admissao: e.target.value })}
                />
              </div>
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
                {editing ? 'Salvar alterações' : 'Criar usuário'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}
