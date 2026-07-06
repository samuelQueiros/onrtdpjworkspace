import { useEffect, useState } from 'react'
import AniversariantesMes from '../components/mural/AniversariantesMes'
import AvisoForm, { blankAvisoForm } from '../components/mural/AvisoForm'
import AvisosLista from '../components/mural/AvisosLista'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { EmptyState, LoadingCard, PageHeader } from './_helpers'

export default function Mural() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const [avisos, setAvisos] = useState([])
  const [aniversariantes, setAniversariantes] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState(blankAvisoForm)
  const [editing, setEditing] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () => {
    const fn = isAdmin ? api.listarTodosAvisos : api.listarAvisos
    return Promise.all([fn(), api.listarAniversariantes().catch(() => [])])
      .then(([avisosData, aniversariantesData]) => {
        setAvisos(avisosData)
        setAniversariantes(aniversariantesData)
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setForm(blankAvisoForm)
    setEditing(null)
    setShowForm(false)
  }

  const save = async event => {
    event.preventDefault()
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
      resetForm()
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

  const toggleForm = () => {
    setShowForm(open => !open)
    setEditing(null)
    setForm(blankAvisoForm)
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Mural de Avisos"
        subtitle="Comunicados e informações importantes para a equipe."
        action={
          isAdmin && (
            <button className="btn btn-primary" onClick={toggleForm}>
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

      <AniversariantesMes aniversariantes={aniversariantes} />

      {isAdmin && showForm && (
        <AvisoForm
          editing={editing}
          form={form}
          onCancel={resetForm}
          onChange={setForm}
          onSubmit={save}
        />
      )}

      <section className="card">
        <div className="card-body avisos-lista">
          {avisos.length ? (
            <AvisosLista
              avisos={avisos}
              isAdmin={isAdmin}
              onDelete={excluir}
              onEdit={startEdit}
            />
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
