import { useCallback, useEffect, useRef, useState } from 'react'
import '../styles/pages/usuarios.css'
import DetalhesUsuarioModal from '../components/usuarios/DetalhesUsuarioModal'
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
  const [details, setDetails] = useState(null)
  const [detailsLoadingId, setDetailsLoadingId] = useState(null)
  const [fichaImporting, setFichaImporting] = useState(false)
  const [fichaDownloading, setFichaDownloading] = useState(false)
  const [fichaSaving, setFichaSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [downloadingModel, setDownloadingModel] = useState(false)
  const importFileRef = useRef(null)

  const load = useCallback(() =>
    Promise.all([api.listarUsuarios(), api.listarDepartamentos(), api.listarCargos()])
      .then(([usuarios, deps, listaCargos]) => {
        setUsers(usuarios)
        setDepartamentos(deps)
        setCargos(listaCargos)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false)), [toast])

  useEffect(() => { load() }, [load])

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
        proxima_concessao_ferias: form.proxima_concessao_ferias || null,
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
        payload.saldo_atual_dias = Number(form.saldo_atual_dias)
        if (form.motivo_ajuste_saldo.trim()) payload.motivo_ajuste_saldo = form.motivo_ajuste_saldo.trim()
        await api.editarUsuario(editing, payload)
        toast.success('Usuário atualizado com sucesso.')
      } else {
        payload.senha = form.senha
        payload.role = form.role
        payload.saldo_inicial_dias = Number(form.saldo_inicial_dias)
        await api.criarUsuario(payload)
        toast.success('Usuário criado com sucesso.')
      }
      closeModal()
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const startEdit = async (user, loadedSensitive = null) => {
    try {
      const sensitive = loadedSensitive || await api.obterDadosSensiveisUsuario(user.id)
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
      saldo_inicial_dias: 30,
      saldo_atual_dias: user.dias_restantes,
      motivo_ajuste_saldo: '',
      proxima_concessao_ferias: user.proxima_concessao_ferias || '',
      })
      setModalOpen(true)
    } catch (error) {
      toast.error(error.message)
    }
  }

  const showDetails = async user => {
    setDetailsLoadingId(user.id)
    try {
      const [sensitive, ficha] = await Promise.all([
        api.obterDadosSensiveisUsuario(user.id),
        api.obterFichaAdmissional(user.id),
      ])
      setDetails({ user, sensitive, ficha })
    } catch (error) {
      toast.error(error.message)
    } finally {
      setDetailsLoadingId(null)
    }
  }

  const editFromDetails = () => {
    const selected = details
    setDetails(null)
    if (selected) startEdit(selected.user, selected.sensitive)
  }

  const downloadFichaModel = async () => {
    if (!details) return
    setFichaDownloading(true)
    try {
      const blob = await api.baixarModeloFichaAdmissional(details.user.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `ficha-admissional-${details.user.id}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setFichaDownloading(false)
    }
  }

  const importFicha = async file => {
    if (!details || !file) return
    const userId = details.user.id
    setFichaImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resultado = await api.importarFichaAdmissional(userId, formData)
      setDetails(current => (
        current?.user.id === userId ? { ...current, ficha: resultado.ficha } : current
      ))
      toast.success(resultado.mensagem)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setFichaImporting(false)
    }
  }

  const saveFicha = async payload => {
    if (!details) return
    const userId = details.user.id
    setFichaSaving(true)
    try {
      const ficha = await api.editarFichaAdmissional(userId, payload)
      setDetails(current => (
        current?.user.id === userId ? { ...current, ficha } : current
      ))
      toast.success('Ficha admissional atualizada com sucesso.')
    } catch (error) {
      toast.error(error.message)
      throw error
    } finally {
      setFichaSaving(false)
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

  const exportar = async () => {
    setExporting(true)
    try {
      const blob = await api.exportarUsuarios()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `colaboradores-${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      toast.success('Planilha de colaboradores exportada com sucesso.')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setExporting(false)
    }
  }

  const baixarModelo = async () => {
    setDownloadingModel(true)
    try {
      const blob = await api.baixarModeloColaboradores()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'modelo-importacao-colaboradores.xlsx'
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setDownloadingModel(false)
    }
  }

  const importar = async event => {
    const file = event.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resultado = await api.importarColaboradores(formData)
      if (resultado.erros?.length) {
        toast.error(`${resultado.mensagem} ${resultado.erros.slice(0, 3).join(' · ')}`)
      } else {
        toast.success(resultado.mensagem)
        await load()
      }
    } catch (error) {
      toast.error(error.message)
    } finally {
      setImporting(false)
      if (importFileRef.current) importFileRef.current.value = ''
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Colaboradores"
        subtitle="Cadastre colaboradores, ajuste saldos e defina cores de identificação."
        action={
          <div className="users-header-actions">
            <button
              className="btn btn-outline"
              type="button"
              onClick={baixarModelo}
              disabled={downloadingModel}
            >
              {downloadingModel ? 'Baixando...' : 'Baixar modelo'}
            </button>
            <label className="btn btn-outline clickable-label">
              {importing ? 'Importando...' : 'Importar Excel'}
              <input
                ref={importFileRef}
                type="file"
                accept=".xlsx"
                className="hidden-input"
                onChange={importar}
                disabled={importing}
              />
            </label>
            <button
              className="btn btn-outline"
              type="button"
              onClick={exportar}
              disabled={exporting || !users.length}
            >
              {exporting ? 'Exportando...' : 'Exportar Excel'}
            </button>
            <button className="btn btn-primary" type="button" onClick={startCreate}>+ Cadastrar Colaborador</button>
          </div>
        }
      />

      <UsersTable
        users={users}
        currentUserId={currentUser?.id}
        detailsLoadingId={detailsLoadingId}
        onDetails={showDetails}
        onEdit={startEdit}
        onDelete={excluir}
        onReactivate={reativar}
      />

      {details && (
        <DetalhesUsuarioModal
          user={details.user}
          sensitive={details.sensitive}
          ficha={details.ficha}
          fichaImporting={fichaImporting}
          fichaDownloading={fichaDownloading}
          fichaSaving={fichaSaving}
          onClose={() => setDetails(null)}
          onDownloadTemplate={downloadFichaModel}
          onEdit={editFromDetails}
          onImportFicha={importFicha}
          onSaveFicha={saveFicha}
        />
      )}

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
