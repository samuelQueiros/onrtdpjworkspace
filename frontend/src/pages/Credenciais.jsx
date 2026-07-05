import { useEffect, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader } from './_helpers'

const blank = { descricao: '', email: '', senha: '' }

export default function Credenciais() {
  const [credenciais, setCredenciais] = useState([])
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [mostrarSenha, setMostrarSenha] = useState(false)

  const [usuarios, setUsuarios] = useState([])
  const [userIds, setUserIds] = useState([])

  const load = () =>
    api.listarCredenciais()
      .then(setCredenciais)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const carregarUsuarios = async (credencialId) => {
    const lista = await api.usuariosCredencial(credencialId)
    setUsuarios(lista)
    setUserIds(lista.filter(u => u.tem_acesso).map(u => u.id))
  }

  const startEdit = async (c) => {
    setEditing(c.id)
    setForm({ descricao: c.descricao, email: c.email, senha: '' })
    setError('')
    setSuccess('')
    setMostrarSenha(false)
    await carregarUsuarios(c.id)
  }

  const startNova = async () => {
    setEditing('nova')
    setForm(blank)
    setError('')
    setSuccess('')
    setMostrarSenha(false)
    try {
      const lista = await api.listarUsuarios()
      setUsuarios(lista.map(u => ({ ...u, tem_acesso: false })))
      setUserIds([])
    } catch {
      setUsuarios([])
      setUserIds([])
    }
  }

  const cancelar = () => {
    setEditing(null)
    setForm(blank)
    setUsuarios([])
    setUserIds([])
    setError('')
    setSuccess('')
  }

  const toggleUsuario = (id) => {
    setUserIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const save = async e => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      if (editing === 'nova') {
        const nova = await api.criarCredencial(form)
        if (userIds.length > 0) {
          await api.salvarPermissoes(nova.id, userIds)
        }
        setSuccess('Credencial criada com sucesso.')
      } else {
        await api.editarCredencial(editing, form)
        await api.salvarPermissoes(editing, userIds)
        setSuccess('Credencial atualizada com sucesso.')
      }
      setEditing(null)
      setForm(blank)
      setUsuarios([])
      setUserIds([])
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const excluir = async id => {
    if (!confirm('Excluir esta credencial e todos os acessos associados?')) return
    setError('')
    try {
      await api.excluirCredencial(id)
      setSuccess('Credencial excluída.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Acessos / Senhas"
        subtitle="Gerencie credenciais compartilhadas e controle quem tem acesso a cada uma."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">Credenciais cadastradas</h2>
            {!editing && (
              <button className="btn btn-primary btn-sm" onClick={startNova}>
                + Nova Credencial
              </button>
            )}
          </div>
          <div className="table-wrap">
            {credenciais.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th>E-mail</th>
                    <th>Usuários com acesso</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {credenciais.map(c => (
                    <tr key={c.id}>
                      <td><strong>{c.descricao}</strong></td>
                      <td>{c.email}</td>
                      <td>{c.total_usuarios} {c.total_usuarios === 1 ? 'usuário' : 'usuários'}</td>
                      <td className="actions-cell">
                        <button className="btn btn-outline btn-sm" onClick={() => startEdit(c)}>
                          Editar
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => excluir(c.id)}>
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="Nenhuma credencial cadastrada"
                text="Cadastre credenciais para compartilhar acessos com a equipe."
              />
            )}
          </div>
        </section>

        {editing && (
          <form className="card form-card" onSubmit={save}>
            <div className="card-header">
              <h2 className="card-title">{editing === 'nova' ? 'Nova credencial' : 'Editar credencial'}</h2>
            </div>
            <div className="card-body form-stack">
              {error && <div className="alert alert-error">{error}</div>}
              {success && <div className="alert alert-success">{success}</div>}

              <div className="form-group">
                <label>Descrição</label>
                <input
                  type="text"
                  value={form.descricao}
                  onChange={e => setForm({ ...form, descricao: e.target.value })}
                  placeholder="Ex.: Google Workspace, Meta Business..."
                  required
                />
              </div>

              <div className="form-group">
                <label>E-mail</label>
                <input
                  type="text"
                  value={form.email}
                  onChange={e => setForm({ ...form, email: e.target.value })}
                  placeholder="usuario@empresa.com"
                  required
                />
              </div>

              <div className="form-group">
                <label>Senha</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  <input
                    type={mostrarSenha ? 'text' : 'password'}
                    value={form.senha}
                    onChange={e => setForm({ ...form, senha: e.target.value })}
                    placeholder={editing === 'nova' ? 'Senha de acesso' : 'Deixe em branco para manter a senha atual'}
                    required={editing === 'nova'}
                    style={{ flex: 1 }}
                  />
                  <button
                    type="button"
                    className="btn btn-outline btn-sm"
                    onClick={() => setMostrarSenha(v => !v)}
                    style={{ whiteSpace: 'nowrap' }}
                  >
                    {mostrarSenha ? 'Ocultar' : 'Mostrar'}
                  </button>
                </div>
              </div>

              {usuarios.length > 0 && (
                <div className="form-group">
                  <label>Permissões</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
                    {usuarios.map(u => (
                      <label key={u.id} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontWeight: 'normal' }}>
                        <input
                          type="checkbox"
                          checked={userIds.includes(u.id)}
                          onChange={() => toggleUsuario(u.id)}
                        />
                        {u.nome}
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="button-row">
                <button className="btn btn-outline" type="button" onClick={cancelar}>
                  Cancelar
                </button>
                <button className="btn btn-primary" type="submit">
                  {editing === 'nova' ? 'Criar credencial' : 'Salvar alterações'}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </>
  )
}
