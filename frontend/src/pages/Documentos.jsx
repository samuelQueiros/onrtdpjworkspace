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

  const [historico, setHistorico] = useState({
    recebidos_pessoais: [],
    recebidos_administracao: [],
    enviados: [],
  })
  const [aba, setAba] = useState('recebidos')
  const [escopoRecebidos, setEscopoRecebidos] = useState('pessoal')
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [tipo, setTipo] = useState('atestado')
  const [destinoTipo, setDestinoTipo] = useState(isAdmin ? 'usuario' : 'administracao')
  const [targetUser, setTargetUser] = useState('')
  const fileRef = useRef(null)

  const loadDocs = async () => {
    try {
      setHistorico(await api.historicoDocumentos())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const init = async () => {
      if (isAdmin) setUsers(await api.listarUsuarios())
      await loadDocs()
    }
    init()
  }, [])

  const handleUserFilter = uid => {
    setSelectedUser(uid)
  }

  const handleUpload = async event => {
    event.preventDefault()
    const file = fileRef.current?.files?.[0]
    if (!file) return toast.error('Selecione um arquivo.')

    const uid = isAdmin && destinoTipo === 'usuario' ? targetUser : user.id
    if (!uid) return toast.error('Selecione o destinatário.')

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tipo', tipo)
      formData.append('user_id', uid)
      formData.append('destino_tipo', destinoTipo)
      await api.uploadDocumento(formData)
      toast.success('Documento enviado com sucesso.')
      if (fileRef.current) fileRef.current.value = ''
      await loadDocs()
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
      await loadDocs()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const baixar = async id => {
    try {
      const blob = await api.downloadDocumento(id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const doc = [
        ...historico.recebidos_pessoais,
        ...historico.recebidos_administracao,
        ...historico.enviados,
      ].find(item => item.id === id)
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

  const docsAba = aba === 'enviados'
    ? historico.enviados
    : historico[escopoRecebidos === 'administracao' ? 'recebidos_administracao' : 'recebidos_pessoais']
  const docs = docsAba.filter(doc => (
    !isAdmin || !selectedUser || String(doc.user_id) === String(selectedUser)
  ))

  return (
    <>
      <PageHeader
        title="Documentos"
        subtitle="Documentos pessoais e da caixa geral da administração."
      />

      <div className="grid-2 grid-2-wide-left">
        <DocumentosTabela
          docs={docs}
          aba={aba}
          isAdmin={isAdmin}
          loading={loading}
          escopoRecebidos={escopoRecebidos}
          onDelete={excluir}
          onDownload={baixar}
          onAbaChange={setAba}
          onEscopoRecebidosChange={setEscopoRecebidos}
          onUserFilter={handleUserFilter}
          selectedUser={selectedUser}
          users={users}
        />

        <UploadDocumentoForm
          fileRef={fileRef}
          isAdmin={isAdmin}
          onSubmit={handleUpload}
          destinoTipo={destinoTipo}
          onDestinoTipoChange={setDestinoTipo}
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
