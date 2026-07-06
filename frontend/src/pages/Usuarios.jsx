import { useEffect, useState } from 'react'
import UserForm, { blankUserForm } from '../components/usuarios/UserForm'
import UsersTable from '../components/usuarios/UsersTable'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Usuarios() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [form, setForm] = useState(blankUserForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const load = () =>
    Promise.all([api.listarUsuarios(), api.listarDepartamentos()])
      .then(([usuarios, deps]) => { setUsers(usuarios); setDepartamentos(deps) })
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setForm(blankUserForm)
    setEditing(null)
    setError('')
    setSuccess('')
  }

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
        data_aniversario: form.data_aniversario || null,
        cor: form.cor || null,
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
      setForm(blankUserForm)
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
      data_aniversario: user.data_aniversario || '',
      cor: user.cor || '',
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
      <PageHeader title="Usuários" subtitle="Cadastre colaboradores, ajuste saldos e defina cores de identificação." />

      <div className="grid-2 grid-2-wide-left">
        <UsersTable
          users={users}
          currentUserId={currentUser?.id}
          onEdit={startEdit}
          onDelete={excluir}
        />

        <UserForm
          departamentos={departamentos}
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
