import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'
import { useAuth } from '../context/AuthContext'

const TIPO_LABEL = { atestado: 'Atestado', contracheque: 'Contracheque' }
const TIPO_TONE = { atestado: 'blue', contracheque: 'green' }

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function Documentos() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const [docs, setDocs] = useState([])
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [tipo, setTipo] = useState('atestado')
  const [targetUser, setTargetUser] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileRef = useRef(null)

  const loadDocs = async (uid = null) => {
    try {
      if (uid && isAdmin) {
        const data = await api.documentosUsuario(uid)
        setDocs(data)
      } else if (isAdmin && !uid) {
        setDocs([])
      } else {
        const data = await api.meusDocumentos()
        setDocs(data)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const init = async () => {
      if (isAdmin) {
        const u = await api.listarUsuarios()
        setUsers(u)
      }
      await loadDocs(null)
    }
    init()
  }, [])

  const handleUserFilter = async uid => {
    setSelectedUser(uid)
    setLoading(true)
    await loadDocs(uid || null)
  }

  const handleUpload = async e => {
    e.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return setError('Selecione um arquivo.')

    const uid = isAdmin ? (targetUser || user.id) : user.id
    if (!uid) return setError('Selecione o colaborador.')

    setError('')
    setSuccess('')
    setUploading(true)

    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('tipo', tipo)
      fd.append('user_id', uid)
      await api.uploadDocumento(fd)
      setSuccess('Documento enviado com sucesso.')
      if (fileRef.current) fileRef.current.value = ''
      await loadDocs(isAdmin ? selectedUser : null)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const excluir = async id => {
    if (!confirm('Excluir este documento?')) return
    setError('')
    try {
      await api.excluirDocumento(id)
      setSuccess('Documento excluído.')
      await loadDocs(isAdmin ? selectedUser : null)
    } catch (err) {
      setError(err.message)
    }
  }

  const baixar = async id => {
    try {
      const BASE = import.meta.env.VITE_API_URL || 'http://chat-server:8000'
      const token = localStorage.getItem('token')
      const res = await fetch(`${BASE}/documentos/${id}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      const doc = docs.find(d => d.id === id)
      a.href = url
      a.download = doc?.nome_arquivo || 'documento'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch {
      setError('Erro ao baixar o documento.')
    }
  }

  return (
    <>
      <PageHeader
        title="Documentos"
        subtitle="Atestados médicos e contracheques dos colaboradores."
      />

      {(error || success) && (
        <div className={`alert spaced ${error ? 'alert-error' : 'alert-success'}`}>
          {error || success}
        </div>
      )}

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          {isAdmin && (
            <div className="card-header">
              <h2 className="card-title">Documentos</h2>
              <select
                value={selectedUser}
                onChange={e => handleUserFilter(e.target.value)}
                className="select-filter"
              >
                <option value="">Selecione um colaborador...</option>
                {users.map(u => (
                  <option key={u.id} value={u.id}>{u.nome}</option>
                ))}
              </select>
            </div>
          )}
          {!isAdmin && (
            <div className="card-header"><h2 className="card-title">Meus documentos</h2></div>
          )}
          <div className="table-wrap">
            {loading ? (
              <div className="empty"><div className="spinner" /><p>Carregando...</p></div>
            ) : docs.length ? (
              <table>
                <thead>
                  <tr>
                    <th>Tipo</th>
                    <th>Arquivo</th>
                    <th>Tamanho</th>
                    <th>Enviado por</th>
                    <th>Data</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {docs.map(doc => (
                    <tr key={doc.id}>
                      <td>
                        <StatusBadge tone={TIPO_TONE[doc.tipo] || 'gray'}>
                          {TIPO_LABEL[doc.tipo] || doc.tipo}
                        </StatusBadge>
                      </td>
                      <td>{doc.nome_arquivo}</td>
                      <td>{formatBytes(doc.tamanho)}</td>
                      <td>{doc.criado_por_nome}</td>
                      <td>{formatDate(doc.criado_em)}</td>
                      <td className="actions-cell">
                        <button className="btn btn-outline btn-sm" onClick={() => baixar(doc.id)}>
                          Download
                        </button>
                        {isAdmin && (
                          <button className="btn btn-danger btn-sm" onClick={() => excluir(doc.id)}>
                            Excluir
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState
                title="Nenhum documento"
                text={isAdmin && !selectedUser ? 'Selecione um colaborador para ver seus documentos.' : 'Nenhum documento encontrado.'}
              />
            )}
          </div>
        </section>

        <form className="card form-card" onSubmit={handleUpload}>
          <div className="card-header"><h2 className="card-title">Enviar documento</h2></div>
          <div className="card-body form-stack">
            <div className="form-group">
              <label>Tipo de documento</label>
              <select value={tipo} onChange={e => setTipo(e.target.value)}>
                <option value="atestado">Atestado médico</option>
                {isAdmin && <option value="contracheque">Contracheque</option>}
              </select>
            </div>

            {isAdmin && (
              <div className="form-group">
                <label>Colaborador</label>
                <select
                  value={targetUser}
                  onChange={e => setTargetUser(e.target.value)}
                  required
                >
                  <option value="">Selecione...</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>{u.nome}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <label>Arquivo (PDF, JPG, PNG — máx. 10 MB)</label>
              <input ref={fileRef} type="file" accept=".pdf,.jpg,.jpeg,.png,.gif,.webp" required />
            </div>

            <button className="btn btn-primary" type="submit" disabled={uploading}>
              {uploading ? 'Enviando...' : 'Enviar documento'}
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
