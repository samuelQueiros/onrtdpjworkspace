import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/aprovacoes.css'
import '../styles/pages/aprovacoes-equipamentos.css'
import FiltrosAprovacoes from '../components/aprovacoes/FiltrosAprovacoes'
import RejeitarFeriasModal from '../components/aprovacoes/RejeitarFeriasModal'
import TabelaAprovacoes from '../components/aprovacoes/TabelaAprovacoes'
import AutorizacoesEquipamentosPainel from '../components/aprovacoesEquipamentos/AutorizacoesEquipamentosPainel'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Aprovacoes() {
  const toast = useToast()
  const [aba, setAba] = useState('ferias')
  const [equipamentosAtivados, setEquipamentosAtivados] = useState(false)
  const [todas, setTodas] = useState([])
  const [loading, setLoading] = useState(true)
  const [rejeitando, setRejeitando] = useState(null)
  const [filtro, setFiltro] = useState('pendente')
  const [equipamentosPendentes, setEquipamentosPendentes] = useState(0)

  const load = useCallback(() => {
    setLoading(true)
    return api.todasFerias()
      .then(setTodas)
      .catch(err => toast.error(err.message))
      .finally(() => setLoading(false))
  }, [toast])

  const loadPendingCounts = useCallback(() => api.pendenciasAprovacoes()
    .then(data => setEquipamentosPendentes(data.equipamentos || 0))
    .catch(error => console.error('Falha ao atualizar contadores de aprovações', error)), [])

  useEffect(() => {
    load()
    loadPendingCounts()
    window.addEventListener('approvals:changed', loadPendingCounts)
    return () => window.removeEventListener('approvals:changed', loadPendingCounts)
  }, [load, loadPendingCounts])

  const aprovar = async id => {
    try {
      await api.aprovarFerias(id)
      toast.success('Férias aprovadas com sucesso.')
      window.dispatchEvent(new Event('approvals:changed'))
      await load()
    } catch (err) {
      toast.error(err.message)
    }
  }

  const selectTab = next => {
    setAba(next)
    if (next === 'equipamentos') setEquipamentosAtivados(true)
  }

  const handleTabKeyDown = (event, current) => {
    if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return
    event.preventDefault()
    const next = current === 'ferias' ? 'equipamentos' : 'ferias'
    selectTab(next)
    window.requestAnimationFrame(() => document.getElementById(`tab-aprovacoes-${next}`)?.focus())
  }

  const filtradas = todas.filter(ferias => (
    filtro === 'todas' ? true : ferias.status === filtro
  ))

  const counts = {
    pendente: todas.filter(ferias => ferias.status === 'pendente').length,
    aprovada: todas.filter(ferias => ferias.status === 'aprovada').length,
    rejeitada: todas.filter(ferias => ferias.status === 'rejeitada').length,
    todas: todas.length,
  }

  return (
    <>
      <PageHeader
        title="Aprovações"
        subtitle="Gerencie solicitações de férias e autorizações de equipamentos em fluxos independentes."
      />

      <div className="approval-domain-tabs" role="tablist" aria-label="Tipos de aprovação">
        <button
          id="tab-aprovacoes-ferias"
          className={`approval-domain-tab${aba === 'ferias' ? ' active' : ''}`}
          type="button"
          role="tab"
          aria-selected={aba === 'ferias'}
          aria-controls="painel-aprovacoes-ferias"
          tabIndex={aba === 'ferias' ? 0 : -1}
          onClick={() => selectTab('ferias')}
          onKeyDown={event => handleTabKeyDown(event, 'ferias')}
        >
          Férias
          {counts.pendente > 0 && <span>{counts.pendente}</span>}
        </button>
        <button
          id="tab-aprovacoes-equipamentos"
          className={`approval-domain-tab${aba === 'equipamentos' ? ' active' : ''}`}
          type="button"
          role="tab"
          aria-selected={aba === 'equipamentos'}
          aria-controls="painel-aprovacoes-equipamentos"
          tabIndex={aba === 'equipamentos' ? 0 : -1}
          onClick={() => selectTab('equipamentos')}
          onKeyDown={event => handleTabKeyDown(event, 'equipamentos')}
        >
          Equipamentos
          {equipamentosPendentes > 0 && <span>{equipamentosPendentes}</span>}
        </button>
      </div>

      <section
        id="painel-aprovacoes-ferias"
        role="tabpanel"
        aria-labelledby="tab-aprovacoes-ferias"
        hidden={aba !== 'ferias'}
      >
        {loading ? <LoadingCard /> : (
          <>
            <FiltrosAprovacoes counts={counts} filtro={filtro} onChange={setFiltro} />
            <TabelaAprovacoes
              filtro={filtro}
              ferias={filtradas}
              onAprovar={aprovar}
              onRejeitar={setRejeitando}
            />
          </>
        )}
      </section>

      <section
        id="painel-aprovacoes-equipamentos"
        role="tabpanel"
        aria-labelledby="tab-aprovacoes-equipamentos"
        hidden={aba !== 'equipamentos'}
      >
        {equipamentosAtivados && <AutorizacoesEquipamentosPainel />}
      </section>

      {rejeitando && (
        <RejeitarFeriasModal
          ferias={rejeitando}
          onClose={() => setRejeitando(null)}
          onRejeitado={() => {
            setRejeitando(null)
            toast.success('Férias rejeitadas.')
            window.dispatchEvent(new Event('approvals:changed'))
            load()
          }}
        />
      )}
    </>
  )
}
