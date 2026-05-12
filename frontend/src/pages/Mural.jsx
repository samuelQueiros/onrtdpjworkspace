import { useEffect, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'
import { useAuth } from '../context/AuthContext'

const blank = { titulo: '', conteudo: '', fixado: false, data_expiracao: '' }

const AVATAR_COLORS = [
  '#4f86c6', '#e07b54', '#5aab7f', '#a06bbf',
  '#c4a93e', '#d9534f', '#5bc0de', '#3d8b6e',
]

function getInitials(nome) {
  const parts = nome.trim().split(/\s+/)
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

function avatarColor(nome) {
  let hash = 0
  for (const c of nome) hash = (hash * 31 + c.charCodeAt(0)) & 0xffff
  return AVATAR_COLORS[hash % AVATAR_COLORS.length]
}

function BirthdayAvatar({ nome }) {
  return (
    <div className="birthday-avatar" style={{ background: avatarColor(nome) }}>
      {getInitials(nome)}
    </div>
  )
}

function AvisoItem({ aviso, isAdmin, onEdit, onDelete }) {
  return (
    <div className={`aviso-card${aviso.fixado ? ' aviso-fixado' : ''}`}>
      <div className="aviso-header">
        <div className="aviso-titulo-row">
          {aviso.fixado && <span className="badge badge-amber">📌 Fixado</span>}
          <strong>{aviso.titulo}</strong>
        </div>
        {isAdmin && (
          <div className="button-row">
            <button className="btn btn-outline btn-sm" onClick={() => onEdit(aviso)}>Editar</button>
            <button className="btn btn-danger btn-sm" onClick={() => onDelete(aviso.id)}>Excluir</button>
          </div>
        )}
      </div>
      <p className="aviso-corpo">{aviso.conteudo}</p>
      <small className="muted">
        Publicado por <strong>{aviso.criado_por_nome}</strong> em {formatDate(aviso.criado_em)}
        {aviso.data_expiracao && ` · Expira em ${formatDate(aviso.data_expiracao)}`}
      </small>
    </div>
  )
}

export default function Mural() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const [avisos, setAvisos] = useState([])
  const [aniversariantes, setAniversariantes] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(blank)
  const [editing, setEditing] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () => {
    const fn = isAdmin ? api.listarTodosAvisos : api.listarAvisos
    return Promise.all([fn(), api.listarAniversariantes().catch(() => [])])
      .then(([avisos, aniversariantes]) => {
        setAvisos(avisos)
        setAniversariantes(aniversariantes)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const save = async e => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      const payload = {
        titulo: form.titulo,
        conteudo: form.conteudo,
        fixado: form.fixado,
        data_expiracao: form.data_expiracao || null,
      }
      if (editing) {
        await api.editarAviso(editing, payload)
        setSuccess('Aviso atualizado com sucesso.')
      } else {
        await api.criarAviso(payload)
        setSuccess('Aviso publicado com sucesso.')
      }
      setForm(blank)
      setEditing(null)
      setShowForm(false)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const startEdit = aviso => {
    setEditing(aviso.id)
    setForm({
      titulo: aviso.titulo,
      conteudo: aviso.conteudo,
      fixado: aviso.fixado,
      data_expiracao: aviso.data_expiracao || '',
    })
    setShowForm(true)
    setError('')
    setSuccess('')
  }

  const excluir = async id => {
    if (!confirm('Excluir este aviso?')) return
    setError('')
    try {
      await api.excluirAviso(id)
      setSuccess('Aviso excluído.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Mural de Avisos"
        subtitle="Comunicados e informações importantes para a equipe."
        action={
          isAdmin && (
            <button
              className="btn btn-primary"
              onClick={() => { setShowForm(!showForm); setEditing(null); setForm(blank) }}
            >
              {showForm ? 'Fechar formulário' : 'Novo aviso'}
            </button>
          )
        }
      />

      {(error || success) && (
        <div className={`alert spaced ${error ? 'alert-error' : 'alert-success'}`}>
          {error || success}
        </div>
      )}

      {aniversariantes.length > 0 && (
        <section className="card spaced">
          <div className="card-header">
            <h2 className="card-title">Aniversariantes do mês</h2>
          </div>
          <div className="card-body">
            <div className="birthday-grid">
              {aniversariantes.map((item, index) => (
                <div key={index} className="birthday-card">
                  <BirthdayAvatar nome={item.nome} />
                  <strong className="birthday-nome">{item.nome}</strong>
                  <span className="birthday-data">🎂 {formatDate(item.data_aniversario)}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {isAdmin && showForm && (
        <section className="card spaced">
          <div className="card-header">
            <h2 className="card-title">{editing ? 'Editar aviso' : 'Publicar novo aviso'}</h2>
          </div>
          <form onSubmit={save}>
            <div className="card-body form-stack">
              <div className="form-group">
                <label>Título</label>
                <input
                  type="text"
                  value={form.titulo}
                  onChange={e => setForm({ ...form, titulo: e.target.value })}
                  placeholder="Título do aviso"
                  required
                />
              </div>
              <div className="form-group">
                <label>Conteúdo</label>
                <textarea
                  value={form.conteudo}
                  onChange={e => setForm({ ...form, conteudo: e.target.value })}
                  rows={4}
                  placeholder="Texto do comunicado..."
                  required
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Data de expiração (opcional)</label>
                  <input
                    type="date"
                    value={form.data_expiracao}
                    onChange={e => setForm({ ...form, data_expiracao: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>&nbsp;</label>
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={form.fixado}
                      onChange={e => setForm({ ...form, fixado: e.target.checked })}
                    />
                    <span>Fixar aviso no topo</span>
                  </label>
                </div>
              </div>
              <div className="button-row">
                <button
                  className="btn btn-outline"
                  type="button"
                  onClick={() => { setShowForm(false); setEditing(null); setForm(blank) }}
                >
                  Cancelar
                </button>
                <button className="btn btn-primary" type="submit">
                  {editing ? 'Salvar alterações' : 'Publicar aviso'}
                </button>
              </div>
            </div>
          </form>
        </section>
      )}

      <section className="card">
        <div className="card-body avisos-lista">
          {avisos.length ? (
            avisos.map(aviso => (
              <AvisoItem
                key={aviso.id}
                aviso={aviso}
                isAdmin={isAdmin}
                onEdit={startEdit}
                onDelete={excluir}
              />
            ))
          ) : (
            <EmptyState
              title="Nenhum aviso publicado"
              text="O administrador publicará comunicados aqui."
            />
          )}
        </div>
      </section>
    </>
  )
}
