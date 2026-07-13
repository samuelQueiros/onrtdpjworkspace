import { useEffect, useState } from 'react'
import '../styles/pages/usuarios.css'
import UserForm, { blankUserForm } from '../components/usuarios/UserForm'
import UsersTable from '../components/usuarios/UsersTable'
import { useAuth } from '../contexts/AuthContext'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Usuarios() {
  const { user: currentUser } = useAuth()
  const confirmar = useConfirm()
  const toast = useToast()
  const [users, setUsers] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [cargos, setCargos] = useState([])
  const [form, setForm] = useState(blankUserForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () =>
    Promise.all([api.listarUsuarios(), api.listarDepartamentos(), api.listarCargos()])
      .then(([usuarios, deps, listaCargos]) => {
        setUsers(usuarios)
        setDepartamentos(deps)
        setCargos(listaCargos)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setForm(blankUserForm)
    setEditing(null)
  }

  const save = async event => {
    event.preventDefault()
    try {
      const payload = {
        nome: form.nome,
        email: form.email,
        dias_totais: Number(form.dias_totais),
        departamento_id: form.departamento_id ? Number(form.departamento_id) : null,
        data_admissao: form.data_admissao || null,
        data_aniversario: form.data_aniversario || null,
        cor: form.cor || null,
        telefone: form.telefone || null,
        telefone_emergencia: form.telefone_emergencia || null,
        endereco: Object.values(form.endereco).some(value => value.trim()) ? form.endereco : null,
        dados_bancarios: Object.values(form.dados_bancarios).some(value => value.trim())
          ? form.dados_bancarios
          : null,
        cargo: form.cargo || null,
      }
      if (editing) {
        if (form.senha) payload.senha = form.senha
        await api.editarUsuario(editing, payload)
        toast.success('Usuário atualizado com sucesso.')
      } else {
        payload.senha = form.senha
        payload.role = form.role
        await api.criarUsuario(payload)
        toast.success('Usuário criado com sucesso.')
      }
      setForm(blankUserForm)
      setEditing(null)
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const startEdit = async user => {
    try {
      const sensitive = await api.obterDadosSensiveisUsuario(user.id)
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
      telefone: user.telefone || '',
      telefone_emergencia: sensitive.telefone_emergencia || '',
      endereco: {
        ...blankUserForm.endereco,
        ...(sensitive.endereco || {}),
      },
      dados_bancarios: {
        ...blankUserForm.dados_bancarios,
        ...(sensitive.dados_bancarios || {}),
      },
      cargo: user.cargo || '',
      })
    } catch (error) {
      toast.error(error.message)
    }
  }

  const excluir = async id => {
    const confirmado = await confirmar({
      title: 'Desativar colaborador?',
      message: 'O acesso será bloqueado, mas o histórico e os documentos serão preservados.',
      confirmLabel: 'Desativar colaborador',
    })
    if (!confirmado) return

    try {
      await api.excluirUsuario(id)
      toast.success('Colaborador desativado.')
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const reativar = async id => {
    try {
      await api.reativarUsuario(id)
      toast.success('Colaborador reativado.')
      await load()
    } catch (error) {
      toast.error(error.message)
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
          onReactivate={reativar}
        />

        <UserForm
          departamentos={departamentos}
          cargos={cargos}
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
