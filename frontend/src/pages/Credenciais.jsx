import { useEffect, useState } from 'react'
import CredencialForm, { blankCredencialForm } from '../components/credenciais/CredencialForm'
import CredenciaisTabela from '../components/credenciais/CredenciaisTabela'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Credenciais() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [credenciais, setCredenciais] = useState([])
  const [form, setForm] = useState(blankCredencialForm)
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)
  const [mostrarSenha, setMostrarSenha] = useState(false)
  const [usuarios, setUsuarios] = useState([])
  const [userIds, setUserIds] = useState([])

  const load = () =>
    api.listarCredenciais()
      .then(setCredenciais)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const carregarUsuarios = async credencialId => {
    const lista = await api.usuariosCredencial(credencialId)
    setUsuarios(lista)
    setUserIds(lista.filter(usuario => usuario.tem_acesso).map(usuario => usuario.id))
  }

  const startEdit = async credencial => {
    setEditing(credencial.id)
    setForm({ descricao: credencial.descricao, email: credencial.email, senha: '' })
    setMostrarSenha(false)
    await carregarUsuarios(credencial.id)
  }

  const startNova = async () => {
    setEditing('nova')
    setForm(blankCredencialForm)
    setMostrarSenha(false)
    try {
      const lista = await api.listarUsuarios()
      setUsuarios(lista.map(usuario => ({ ...usuario, tem_acesso: false })))
      setUserIds([])
    } catch {
      setUsuarios([])
      setUserIds([])
    }
  }

  const cancelar = () => {
    setEditing(null)
    setForm(blankCredencialForm)
    setUsuarios([])
    setUserIds([])
  }

  const toggleUsuario = id => {
    setUserIds(prev =>
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    )
  }

  const save = async event => {
    event.preventDefault()
    try {
      if (editing === 'nova') {
        const nova = await api.criarCredencial(form)
        if (userIds.length > 0) await api.salvarPermissoes(nova.id, userIds)
        toast.success('Credencial criada com sucesso.')
      } else {
        await api.editarCredencial(editing, form)
        await api.salvarPermissoes(editing, userIds)
        toast.success('Credencial atualizada com sucesso.')
      }
      setEditing(null)
      setForm(blankCredencialForm)
      setUsuarios([])
      setUserIds([])
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const excluir = async id => {
    const confirmado = await confirmar({
      title: 'Excluir credencial?',
      message: 'Todos os acessos associados a esta credencial também serão removidos.',
      confirmLabel: 'Excluir credencial',
    })
    if (!confirmado) return

    try {
      await api.excluirCredencial(id)
      toast.success('Credencial excluída.')
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Acessos / Senhas"
        subtitle="Gerencie credenciais compartilhadas e controle quem tem acesso a cada uma."
      />

      <div className="grid-2 grid-2-wide-left">
        <CredenciaisTabela
          credenciais={credenciais}
          editing={editing}
          onDelete={excluir}
          onEdit={startEdit}
          onNew={startNova}
        />

        {editing && (
          <CredencialForm
            editing={editing}
            form={form}
            mostrarSenha={mostrarSenha}
            onCancel={cancelar}
            onChange={setForm}
            onSubmit={save}
            onToggleSenha={() => setMostrarSenha(value => !value)}
            onToggleUsuario={toggleUsuario}
            userIds={userIds}
            usuarios={usuarios}
          />
        )}
      </div>
    </>
  )
}
