import { useEffect, useState } from 'react'
import '../styles/pages/bloqueios.css'
import BloqueioForm, { blankBloqueioForm } from '../components/bloqueios/BloqueioForm'
import BloqueiosTabela from '../components/bloqueios/BloqueiosTabela'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Bloqueios() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [bloqueios, setBloqueios] = useState([])
  const [form, setForm] = useState(blankBloqueioForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState('todos')

  const load = () =>
    api.listarBloqueios()
      .then(setBloqueios)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setEditing(null)
    setForm(blankBloqueioForm)
  }

  const save = async event => {
    event.preventDefault()
    try {
      if (editing) {
        await api.editarBloqueio(editing, form)
        toast.success('Período atualizado com sucesso.')
      } else {
        await api.criarBloqueio(form)
        toast.success('Período cadastrado com sucesso.')
      }
      setForm(blankBloqueioForm)
      setEditing(null)
      await load()
    } catch (err) {
      toast.error(err.message)
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
  }

  const excluir = async id => {
    const confirmado = await confirmar({
      title: 'Excluir bloqueio/recesso?',
      message: 'O período deixará de aparecer como indisponível no calendário.',
      confirmLabel: 'Excluir período',
    })
    if (!confirmado) return

    try {
      await api.excluirBloqueio(id)
      toast.success('Período excluído.')
      await load()
    } catch (err) {
      toast.error(err.message)
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
          form={form}
          onCancel={resetForm}
          onChange={setForm}
          onSubmit={save}
        />
      </div>
    </>
  )
}
