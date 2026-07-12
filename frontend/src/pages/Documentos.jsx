import { useEffect, useRef, useState } from 'react'
import '../styles/pages/documentos.css'
import DocumentosTabela from '../components/documentos/DocumentosTabela'
import UploadDocumentoForm from '../components/documentos/UploadDocumentoForm'
import { useAuth } from '../contexts/AuthContext'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { PageHeader } from '../components/comum/PageHelpers'

export default function Documentos() {
  const { user } = useAuth()
  const confirmar = useConfirm()
  const toast = useToast()
  const isAdmin = user?.role === 'admin'

  const [docs, setDocs] = useState([])
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [tipo, setTipo] = useState('atestado')
  const [targetUser, setTargetUser] = useState('')
  const fileRef = useRef(null)

  const loadDocs = async (uid = null) => {
    try {
      if (uid && isAdmin) {
        setDocs(await api.documentosUsuario(uid))
      } else if (isAdmin && !uid) {
        setDocs([])
      } else {
        setDocs(await api.meusDocumentos())
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const init = async () => {
      if (isAdmin) setUsers(await api.listarUsuarios())
      await loadDocs(null)
    }
    init()
  }, [])

  const handleUserFilter = async uid => {
    setSelectedUser(uid)
    setLoading(true)
    await loadDocs(uid || null)
  }

  const handleUpload = async event => {
    event.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return toast.error('Selecione um arquivo.')

    const uid = isAdmin ? (targetUser || user.id) : user.id
    if (!uid) return toast.error('Selecione o colaborador.')

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tipo', tipo)
      formData.append('user_id', uid)
      await api.uploadDocumento(formData)
      toast.success('Documento enviado com sucesso.')
      if (fileRef.current) fileRef.current.value = ''
      await loadDocs(isAdmin ? selectedUser : null)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setUploading(false)
    }
  }

  const excluir = async id => {
    const confirmado = await confirmar({
      title: 'Excluir documento?',
      message: 'O arquivo deixará de estar disponível para visualização e download.',
      confirmLabel: 'Excluir documento',
    })
    if (!confirmado) return

    try {
      await api.excluirDocumento(id)
      toast.success('Documento excluído.')
      await loadDocs(isAdmin ? selectedUser : null)
    } catch (err) {
      toast.error(err.message)
    }
  }

  const baixar = async id => {
    try {
      const blob = await api.downloadDocumento(id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const doc = docs.find(item => item.id === id)
      link.href = url
      link.download = doc?.nome_arquivo || 'documento'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err.message)
    }
  }

  return (
    <>
      <PageHeader
        title="Documentos"
        subtitle="Atestados médicos e contracheques dos colaboradores."
      />

      <div className="grid-2 grid-2-wide-left">
        <DocumentosTabela
          docs={docs}
          isAdmin={isAdmin}
          loading={loading}
          onDelete={excluir}
          onDownload={baixar}
          onUserFilter={handleUserFilter}
          selectedUser={selectedUser}
          users={users}
        />

        <UploadDocumentoForm
          fileRef={fileRef}
          isAdmin={isAdmin}
          onSubmit={handleUpload}
          onTargetUserChange={setTargetUser}
          onTipoChange={setTipo}
          targetUser={targetUser}
          tipo={tipo}
          uploading={uploading}
          users={users}
        />
      </div>
    </>
  )
}
