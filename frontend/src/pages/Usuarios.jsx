import { useEffect, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, StatusBadge } from './_helpers'

const blank = { nome: '', email: '', senha: '', role: 'user', dias_totais: 30 }

export default function Usuarios() {
  const [users, setUsers] = useState([])
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => api.listarUsuarios().then(setUsers).finally(() => setLoading(false))

  useEffect(() => {
    load()
  }, [])

  const save = async event => {
    event.preventDefault()
    setError('')
    try {
      if (editing) {
        await api.editarUsuario(editing, {
          nome: form.nome,
          email: form.email,
          dias_totais: Number(form.dias_totais),
        })
      } else {
        await api.criarUsuario({ ...form, dias_totais: Number(form.dias_totais) })
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
    setForm({ nome: user.nome, email: user.email, senha: '', role: user.role, dias_totais: user.dias_totais })
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader title="Usuarios" subtitle="Cadastre colaboradores e ajuste saldos anuais de ferias." />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Colaboradores</h2></div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Nome</th><th>Email</th><th>Perfil</th><th>Saldo</th><th>Total</th><th></th></tr></thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.nome}</td>
                    <td>{user.email}</td>
                    <td><StatusBadge tone={user.role === 'admin' ? 'navy' : 'gray'}>{user.role === 'admin' ? 'Admin' : 'Usuario'}</StatusBadge></td>
                    <td>{user.dias_restantes}</td>
                    <td>{user.dias_totais}</td>
                    <td><button className="btn btn-outline btn-sm" onClick={() => startEdit(user)}>Editar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header"><h2 className="card-title">{editing ? 'Editar usuario' : 'Novo usuario'}</h2></div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            <div className="form-group">
              <label>Nome</label>
              <input value={form.nome} onChange={event => setForm({ ...form, nome: event.target.value })} required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={event => setForm({ ...form, email: event.target.value })} required />
            </div>
            {!editing && (
              <div className="form-group">
                <label>Senha</label>
                <input type="password" value={form.senha} onChange={event => setForm({ ...form, senha: event.target.value })} required />
              </div>
            )}
            {!editing && (
              <div className="form-group">
                <label>Perfil</label>
                <select value={form.role} onChange={event => setForm({ ...form, role: event.target.value })}>
                  <option value="user">Usuario</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
            )}
            <div className="form-group">
              <label>Dias totais</label>
              <input type="number" min="0" value={form.dias_totais} onChange={event => setForm({ ...form, dias_totais: event.target.value })} required />
            </div>
            <div className="button-row">
              {editing && <button className="btn btn-outline" type="button" onClick={() => { setEditing(null); setForm(blank) }}>Cancelar</button>}
              <button className="btn btn-primary" type="submit">{editing ? 'Salvar alteracoes' : 'Criar usuario'}</button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}
