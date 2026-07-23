import { useEffect, useState } from 'react'
import '../styles/pages/usuarios.css'
import UserForm, { blankUserForm } from '../components/usuarios/UserForm'
import UsersTable from '../components/usuarios/UsersTable'
import { useAuth } from '../contexts/AuthContext'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useModalFocusTrap } from '../utils/useModalFocusTrap'
import { maskCpf, maskPhone } from '../utils/inputMasks'

function UserModal({ onClose, ...formProps }) {
  const modalRef = useModalFocusTrap(onClose)

  return (
    <div className="modal-overlay user-modal-overlay" role="presentation" onMouseDown={event => event.target === event.currentTarget && onClose()}>
      <div ref={modalRef} className="modal user-modal" role="dialog" aria-modal="true" aria-labelledby="user-modal-title">
        <UserForm {...formProps} onCancel={onClose} />
      </div>
    </div>
  )
}

export default function Usuarios() {
  const { user: currentUser } = useAuth()
  const confirmar = useConfirm()
  const toast = useToast()
  const [users, setUsers] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [cargos, setCargos] = useState([])
  const [form, setForm] = useState(blankUserForm)
  const [editing, setEditing] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
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

  const closeModal = () => {
    setModalOpen(false)
    resetForm()
  }

  const startCreate = () => {
    resetForm()
    setModalOpen(true)
  }

  const save = async event => {
    event.preventDefault()
    try {
      const payload = {
        nome: form.nome,
        email: form.email,
        cpf: maskCpf(form.cpf),
        dias_totais: Number(form.dias_totais),
        departamento_id: form.departamento_id ? Number(form.departamento_id) : null,
        data_admissao: form.data_admissao || null,
        data_aniversario: form.data_aniversario || null,
        cor: form.cor || null,
        telefone: maskPhone(form.telefone) || null,
        telefone_emergencia: maskPhone(form.telefone_emergencia) || null,
        telefone_emergencia_2: maskPhone(form.telefone_emergencia_2) || null,
        endereco: Object.values(form.endereco).some(value => value.trim()) ? form.endereco : null,
        dados_bancarios: Object.values(form.dados_bancarios).some(value => value.trim())
          ? { ...form.dados_bancarios, cpf_titular: maskCpf(form.dados_bancarios.cpf_titular) }
          : null,
        cargo: form.cargo || null,
      }
      if (editing) {
        if (form.senha) payload.senha = form.senha
        payload.saldo_manual_dias = form.saldo_manual_dias === '' ? null : Number(form.saldo_manual_dias)
        await api.editarUsuario(editing, payload)
        toast.success('Usuário atualizado com sucesso.')
      } else {
        payload.senha = form.senha
        payload.role = form.role
        await api.criarUsuario(payload)
        toast.success('Usuário criado com sucesso.')
      }
      closeModal()
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
      cpf: maskCpf(sensitive.cpf),
      senha: '',
      role: user.role,
      dias_totais: user.dias_totais,
      departamento_id: user.departamento_id || '',
      data_admissao: user.data_admissao || '',
      data_aniversario: user.data_aniversario || '',
      cor: user.cor || '',
      telefone: maskPhone(user.telefone),
      telefone_emergencia: maskPhone(sensitive.telefone_emergencia),
      telefone_emergencia_2: maskPhone(sensitive.telefone_emergencia_2),
      endereco: {
        ...blankUserForm.endereco,
        ...(sensitive.endereco || {}),
      },
      dados_bancarios: {
        ...blankUserForm.dados_bancarios,
        ...(sensitive.dados_bancarios || {}),
        cpf_titular: maskCpf(sensitive.dados_bancarios?.cpf_titular),
      },
      cargo: user.cargo || '',
      saldo_manual_dias: user.saldo_manual_dias ?? '',
      })
      setModalOpen(true)
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
      <PageHeader
        title="Usuários"
        subtitle="Cadastre colaboradores, ajuste saldos e defina cores de identificação."
        action={<button className="btn btn-primary" type="button" onClick={startCreate}>+ Cadastrar Colaborador</button>}
      />

      <UsersTable
        users={users}
        currentUserId={currentUser?.id}
        onEdit={startEdit}
        onDelete={excluir}
        onReactivate={reativar}
      />

      {modalOpen && (
        <UserModal
          departamentos={departamentos}
          cargos={cargos}
          editing={editing}
          form={form}
          onClose={closeModal}
          onChange={setForm}
          onSubmit={save}
        />
      )}
    </>
  )
}
