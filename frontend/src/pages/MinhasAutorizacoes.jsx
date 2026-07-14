import { useEffect, useState } from 'react'
import '../styles/pages/autorizacoes-equipamentos.css'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import DetalhesAutorizacaoModal from '../components/autorizacoesEquipamentos/DetalhesAutorizacaoModal'
import MinhasAutorizacoesTabela from '../components/autorizacoesEquipamentos/MinhasAutorizacoesTabela'

export default function MinhasAutorizacoes() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [items, setItems] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => api.minhasAutorizacoesEquipamentos()
    .then(data => {
      setItems(data)
      if (selected) setSelected(data.find(item => item.id === selected.id) || null)
    })
    .catch(error => toast.error(error.message))
    .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const cancelar = async item => {
    const ok = await confirmar({
      title: 'Cancelar solicitação?',
      message: `A solicitação #${item.id} deixará de seguir para análise.`,
      confirmLabel: 'Cancelar solicitação',
    })
    if (!ok) return
    try {
      await api.cancelarAutorizacaoEquipamento(item.id, { motivo: 'Cancelada pelo colaborador' })
      toast.success('Solicitação cancelada.')
      window.dispatchEvent(new Event('approvals:changed'))
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

  const aceitar = async (id, body) => {
    try {
      const atualizada = await api.aceitarAutorizacaoEquipamento(id, body)
      toast.success(atualizada.documento_status === 'gerado'
        ? 'Aceite registrado e termo definitivo gerado.'
        : 'Aceite registrado. O documento será finalizado pelo administrador.')
      await load()
    } catch (error) {
      toast.error(error.message)
      throw error
    }
  }

  const obterBlob = async documentoId => api.downloadDocumento(documentoId)

  const visualizar = async documentoId => {
    const preview = window.open('', '_blank')
    if (!preview) {
      toast.error('O navegador bloqueou a nova aba. Permita pop-ups para visualizar o termo.')
      return
    }
    preview.opener = null
    preview.document.title = 'Carregando termo...'
    try {
      const blob = await obterBlob(documentoId)
      const url = URL.createObjectURL(blob)
      preview.location.href = url
      setTimeout(() => URL.revokeObjectURL(url), 60_000)
    } catch (error) {
      preview.close()
      toast.error(error.message)
    }
  }

  const baixar = async (documentoId, solicitacaoId) => {
    try {
      const blob = await obterBlob(documentoId)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `termo-equipamentos-solicitacao-${solicitacaoId}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error(error.message)
    }
  }

  if (loading) return <LoadingCard text="Carregando suas autorizações..." />

  return (
    <>
      <PageHeader
        title="Minhas autorizações"
        subtitle="Acompanhe solicitações, entrega, aceite, termo e devolução dos equipamentos."
        action={<Link className="btn btn-primary" to="/solicitar">Nova solicitação</Link>}
      />
      <MinhasAutorizacoesTabela items={items} onCancel={cancelar} onDetails={setSelected} />
      {selected && (
        <DetalhesAutorizacaoModal
          solicitacao={selected}
          onAccept={aceitar}
          onClose={() => setSelected(null)}
          onDownload={baixar}
          onView={visualizar}
        />
      )}
    </>
  )
}
