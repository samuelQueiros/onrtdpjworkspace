import { useEffect, useState } from 'react'
import BloqueioForm, { blankBloqueioForm } from '../components/bloqueios/BloqueioForm'
import BloqueiosTabela from '../components/bloqueios/BloqueiosTabela'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from './_helpers'

export default function Bloqueios() {
  const [bloqueios, setBloqueios] = useState([])
  const [form, setForm] = useState(blankBloqueioForm)
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

  const resetForm = () => {
    setEditing(null)
    setForm(blankBloqueioForm)
    setError('')
    setSuccess('')
  }

  const save = async event => {
    event.preventDefault()
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
      setForm(blankBloqueioForm)
      setEditing(null)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const startEdit = bloqueio => {
    setEditing(bloqueio.id)
    setForm({
      data_inicio: bloqueio.data_inicio,
      data_fim: bloqueio.data_fim,
      motivo: bloqueio.motivo,
      tipo: bloqueio.tipo,
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

  const filtrados = bloqueios.filter(bloqueio =>
    filtro === 'todos' ? true : bloqueio.tipo === filtro
  )

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Bloqueio de Datas"
        subtitle="Impeça marcação de férias em períodos específicos como auditorias, fechamentos e recessos."
      />

      <div className="grid-2 grid-2-wide-left">
        <BloqueiosTabela
          bloqueios={bloqueios}
          filtro={filtro}
          filtrados={filtrados}
          onDelete={excluir}
          onEdit={startEdit}
          onFilterChange={setFiltro}
        />

        <BloqueioForm
          editing={editing}
          error={error}
          form={form}
          onCancel={resetForm}
          onChange={setForm}
          onSubmit={save}
          success={success}
        />
      </div>
    </>
  )
}
