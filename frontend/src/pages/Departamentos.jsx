import { useEffect, useState } from 'react'
import DepartamentoForm, { blankDepartamentoForm } from '../components/departamentos/DepartamentoForm'
import DepartamentosTabela from '../components/departamentos/DepartamentosTabela'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Departamentos() {
  const [deps, setDeps] = useState([])
  const [form, setForm] = useState(blankDepartamentoForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () => api.listarDepartamentos().then(setDeps).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setEditing(null)
    setForm(blankDepartamentoForm)
    setError('')
    setSuccess('')
  }

  const save = async event => {
    event.preventDefault()
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
      setForm(blankDepartamentoForm)
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
        <DepartamentosTabela
          departamentos={deps}
          onDelete={excluir}
          onEdit={startEdit}
        />

        <DepartamentoForm
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
