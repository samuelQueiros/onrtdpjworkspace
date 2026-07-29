import { useCallback, useEffect, useRef, useState } from 'react'
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

  const [documentos, setDocumentos] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: 10,
    pages: 1,
  })
  const [aba, setAba] = useState('recebidos')
  const [escopoRecebidos, setEscopoRecebidos] = useState('pessoal')
  const [page, setPage] = useState(1)
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [tipo, setTipo] = useState('atestado')
  const [observacao, setObservacao] = useState('')
  const [destinoTipo, setDestinoTipo] = useState(isAdmin ? 'usuario' : 'administracao')
  const [targetUser, setTargetUser] = useState('')
  const fileRef = useRef(null)
  const loadRequestRef = useRef(0)

  const caixa = aba === 'enviados'
    ? 'enviados'
    : escopoRecebidos === 'administracao'
      ? 'recebidos_administracao'
      : 'recebidos_pessoais'
  const filtroUsuario = isAdmin && caixa !== 'recebidos_pessoais' ? selectedUser : ''

  const loadDocs = useCallback(async () => {
    const requestId = ++loadRequestRef.current
    setLoading(true)
    try {
      const data = await api.historicoDocumentos({
        caixa,
        page,
        page_size: 10,
        user_id: filtroUsuario,
      })
      if (requestId !== loadRequestRef.current) return
      if (page > data.pages) {
        setPage(data.pages)
        return
      }
      setDocumentos(data)
    } catch (err) {
      if (requestId === loadRequestRef.current) {
        setDocumentos({
          items: [],
          total: 0,
          page,
          page_size: 10,
          pages: 1,
        })
        toast.error(err.message || 'Não foi possível carregar os documentos.')
      }
    } finally {
      if (requestId === loadRequestRef.current) setLoading(false)
    }
  }, [caixa, filtroUsuario, page, toast])

  useEffect(() => {
    loadDocs()
  }, [loadDocs])

  useEffect(() => {
    if (!isAdmin) return
    api.listarUsuarios()
      .then(setUsers)
      .catch(err => toast.error(err.message || 'Não foi possível carregar os colaboradores.'))
  }, [isAdmin, toast])

  const handleUserFilter = uid => {
    setSelectedUser(uid)
    setPage(1)
  }

  const handleAbaChange = proximaAba => {
    setAba(proximaAba)
    setPage(1)
  }

  const handleEscopoRecebidosChange = escopo => {
    setEscopoRecebidos(escopo)
    setPage(1)
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
      formData.append('observacao', observacao)
      await api.uploadDocumento(formData)
      toast.success('Documento enviado com sucesso.')
      if (fileRef.current) fileRef.current.value = ''
      setObservacao('')
      if (page === 1) await loadDocs()
      else setPage(1)
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
      const doc = documentos.items.find(item => item.id === id)
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
        subtitle="Documentos pessoais e da caixa geral da administração."
      />

      <div className="grid-2 grid-2-wide-left">
        <DocumentosTabela
          docs={documentos.items}
          total={documentos.total}
          page={documentos.page}
          pages={documentos.pages}
          aba={aba}
          isAdmin={isAdmin}
          loading={loading}
          escopoRecebidos={escopoRecebidos}
          onDelete={excluir}
          onDownload={baixar}
          onAbaChange={handleAbaChange}
          onEscopoRecebidosChange={handleEscopoRecebidosChange}
          onPageChange={setPage}
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
          observacao={observacao}
          onObservacaoChange={setObservacao}
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
