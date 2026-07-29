import { useCallback, useEffect, useRef, useState } from 'react'
import { LoadingCard } from '../comum/PageHelpers'
import { useConfirm } from '../../contexts/ConfirmContext'
import { useToast } from '../../contexts/ToastContext'
import { autorizacoesEquipamentosService } from '../../services/dominios/autorizacoesEquipamentosService'
import { documentosService } from '../../services/dominios/documentosService'
import { usersService } from '../../services/dominios/usersService'
import AprovarAutorizacaoModal from './AprovarAutorizacaoModal'
import CancelarAutorizacaoModal from './CancelarAutorizacaoModal'
import DetalhesAutorizacaoModal from './DetalhesAutorizacaoModal'
import DevolucaoAutorizacaoModal from './DevolucaoAutorizacaoModal'
import EntregaAutorizacaoModal from './EntregaAutorizacaoModal'
import FiltrosAutorizacoesEquipamentos from './FiltrosAutorizacoesEquipamentos'
import RejeitarAutorizacaoModal from './RejeitarAutorizacaoModal'
import TabelaAutorizacoesEquipamentos from './TabelaAutorizacoesEquipamentos'

const INITIAL_FILTERS = {
  status: 'pendente',
  user_id: '',
  equipamento_id: '',
  criado_de: '',
  criado_ate: '',
}

const ACTION_SERVICE = {
  aprovar: autorizacoesEquipamentosService.aprovarAutorizacao,
  rejeitar: autorizacoesEquipamentosService.rejeitarAutorizacao,
  registrar_entrega: autorizacoesEquipamentosService.registrarEntregaAutorizacao,
  registrar_devolucao: autorizacoesEquipamentosService.registrarDevolucaoAutorizacao,
  cancelar: autorizacoesEquipamentosService.cancelarAutorizacaoEquipamento,
}

const SUCCESS_MESSAGES = {
  aprovar: 'Autorização aprovada com sucesso.',
  rejeitar: 'Autorização rejeitada.',
  registrar_entrega: 'Entrega registrada. O aceite do colaborador está pendente.',
  registrar_devolucao: 'Devolução registrada com sucesso.',
  cancelar: 'Autorização cancelada e reservas liberadas.',
}

function toApiFilters(filters) {
  return {
    status: filters.status,
    user_id: filters.user_id,
    equipamento_id: filters.equipamento_id,
    criado_de: filters.criado_de ? `${filters.criado_de}T00:00:00-03:00` : '',
    criado_ate: filters.criado_ate ? `${filters.criado_ate}T23:59:59-03:00` : '',
  }
}

export default function AutorizacoesEquipamentosPainel() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [items, setItems] = useState([])
  const [pagination, setPagination] = useState({ page: 1, pages: 0, total: 0 })
  const [users, setUsers] = useState([])
  const [filters, setFilters] = useState(INITIAL_FILTERS)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [modal, setModal] = useState(null)
  const [details, setDetails] = useState(null)
  const [saving, setSaving] = useState(false)
  const [mutatingId, setMutatingId] = useState(null)
  const [downloading, setDownloading] = useState(false)
  const requestSequence = useRef(0)

  const load = useCallback(async (activeFilters, page = 1) => {
    const sequence = ++requestSequence.current
    setLoading(true)
    setError('')
    try {
      const response = await autorizacoesEquipamentosService.listarAutorizacoesAdmin({
        ...toApiFilters(activeFilters),
        page,
        page_size: 25,
      })
      if (sequence === requestSequence.current) {
        setItems(response.items)
        setPagination({ page: response.page, pages: response.pages, total: response.total })
      }
    } catch (err) {
      if (sequence === requestSequence.current) setError(err.message)
    } finally {
      if (sequence === requestSequence.current) setLoading(false)
    }
  }, [])

  useEffect(() => {
    usersService.listarUsuarios().then(setUsers).catch(() => setUsers([]))
    load(INITIAL_FILTERS)
  }, [load])

  const applyFilters = event => {
    event.preventDefault()
    if (filters.criado_de && filters.criado_ate && filters.criado_de > filters.criado_ate) {
      setError('A data inicial não pode ser posterior à data final.')
      return
    }
    load(filters)
  }

  const clearFilters = () => {
    setFilters(INITIAL_FILTERS)
    load(INITIAL_FILTERS)
  }

  const action = async (actionName, autorizacao) => {
    if (actionName !== 'regenerar_documento') {
      setModal({ type: actionName, autorizacao })
      return
    }

    const accepted = await confirmar({
      title: 'Regenerar o termo?',
      message: 'O documento será recomposto com os snapshots e a mesma versão já aceita, preservando o histórico.',
      confirmLabel: 'Gerar termo novamente',
      tone: 'warning',
    })
    if (!accepted) return

    setMutatingId(autorizacao.id)
    try {
      await autorizacoesEquipamentosService.regenerarTermoAutorizacao(autorizacao.id)
      toast.success('Termo regenerado com sucesso.')
      await load(filters)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setMutatingId(null)
    }
  }

  const submitAction = async body => {
    const service = ACTION_SERVICE[modal.type]
    if (!service) return
    setSaving(true)
    setMutatingId(modal.autorizacao.id)
    try {
      await service(modal.autorizacao.id, body)
      toast.success(SUCCESS_MESSAGES[modal.type])
      setModal(null)
      window.dispatchEvent(new Event('approvals:changed'))
      await load(filters)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSaving(false)
      setMutatingId(null)
    }
  }

  const downloadTerm = async autorizacao => {
    setDownloading(true)
    try {
      const blob = await documentosService.downloadDocumento(autorizacao.documento_id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `termo-equipamentos-solicitacao-${autorizacao.id}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setDownloading(false)
    }
  }

  const viewTerm = async autorizacao => {
    const preview = window.open('', '_blank')
    if (!preview) {
      toast.error('O navegador bloqueou a nova aba. Permita pop-ups para visualizar o termo.')
      return
    }
    preview.opener = null
    preview.document.title = 'Carregando termo...'
    setDownloading(true)
    try {
      const blob = await documentosService.downloadDocumento(autorizacao.documento_id)
      const url = URL.createObjectURL(blob)
      preview.location.href = url
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
    } catch (err) {
      preview.close()
      toast.error(err.message)
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="autorizacoes-equipamentos-stack">
      <FiltrosAutorizacoesEquipamentos
        filters={filters}
        loading={loading}
        onChange={setFilters}
        onClear={clearFilters}
        onSubmit={applyFilters}
        users={users}
      />

      {error && (
        <div className="alert alert-error autorizacao-load-error" role="alert">
          <span>{error}</span>
          <button className="btn btn-outline btn-sm" type="button" onClick={() => load(filters)}>Tentar novamente</button>
        </div>
      )}

      {loading && !items.length && !error ? (
        <LoadingCard text="Carregando autorizações de equipamentos..." />
      ) : (
        <>
          <TabelaAutorizacoesEquipamentos
            items={items}
            loading={loading}
            mutatingId={mutatingId}
            onAction={action}
            onDetails={setDetails}
          />
          {pagination.pages > 1 && (
            <nav className="pagination" aria-label="Paginação das autorizações">
              <button
                className="btn btn-outline btn-sm"
                disabled={loading || pagination.page <= 1}
                onClick={() => load(filters, pagination.page - 1)}
                type="button"
              >
                Anterior
              </button>
              <span>Página {pagination.page} de {pagination.pages} · {pagination.total} registros</span>
              <button
                className="btn btn-outline btn-sm"
                disabled={loading || pagination.page >= pagination.pages}
                onClick={() => load(filters, pagination.page + 1)}
                type="button"
              >
                Próxima
              </button>
            </nav>
          )}
        </>
      )}

      {details && (
        <DetalhesAutorizacaoModal
          autorizacao={details}
          downloading={downloading}
          onClose={() => setDetails(null)}
          onDownload={downloadTerm}
          onView={viewTerm}
        />
      )}

      {modal?.type === 'aprovar' && (
        <AprovarAutorizacaoModal autorizacao={modal.autorizacao} onClose={() => setModal(null)} onSubmit={submitAction} saving={saving} />
      )}
      {modal?.type === 'rejeitar' && (
        <RejeitarAutorizacaoModal autorizacao={modal.autorizacao} onClose={() => setModal(null)} onSubmit={submitAction} saving={saving} />
      )}
      {modal?.type === 'registrar_entrega' && (
        <EntregaAutorizacaoModal autorizacao={modal.autorizacao} onClose={() => setModal(null)} onSubmit={submitAction} saving={saving} />
      )}
      {modal?.type === 'registrar_devolucao' && (
        <DevolucaoAutorizacaoModal autorizacao={modal.autorizacao} onClose={() => setModal(null)} onSubmit={submitAction} saving={saving} />
      )}
      {modal?.type === 'cancelar' && (
        <CancelarAutorizacaoModal autorizacao={modal.autorizacao} onClose={() => setModal(null)} onSubmit={submitAction} saving={saving} />
      )}
    </div>
  )
}
