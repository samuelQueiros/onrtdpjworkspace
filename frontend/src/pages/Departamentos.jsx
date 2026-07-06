import { useEffect, useState } from 'react'
import DepartamentoForm, { blankDepartamentoForm } from '../components/departamentos/DepartamentoForm'
import DepartamentosTabela from '../components/departamentos/DepartamentosTabela'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Departamentos() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [deps, setDeps] = useState([])
  const [form, setForm] = useState(blankDepartamentoForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => api.listarDepartamentos().then(setDeps).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setEditing(null)
    setForm(blankDepartamentoForm)
  }

  const save = async event => {
    event.preventDefault()
    try {
      const payload = { nome: form.nome, limite_simultaneo: Number(form.limite_simultaneo) }
      if (editing) {
        await api.editarDepartamento(editing, payload)
        toast.success('Departamento atualizado.')
      } else {
        await api.criarDepartamento(payload)
        toast.success('Departamento criado.')
      }
      setForm(blankDepartamentoForm)
      setEditing(null)
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const excluir = async id => {
    const confirmado = await confirmar({
      title: 'Excluir departamento?',
      message: 'Os usuários vinculados ficarão sem setor. Esta ação não pode ser desfeita.',
      confirmLabel: 'Excluir departamento',
    })
    if (!confirmado) return

    try {
      await api.excluirDepartamento(id)
      toast.success('Departamento excluído.')
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const startEdit = dep => {
    setEditing(dep.id)
    setForm({ nome: dep.nome, limite_simultaneo: dep.limite_simultaneo })
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Departamentos"
        subtitle="Gerencie setores e configure limites de férias simultâneas."
      />

      <div className="grid-2 grid-2-wide-left">
        <DepartamentosTabela
          departamentos={deps}
          onDelete={excluir}
          onEdit={startEdit}
        />

        <DepartamentoForm
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
