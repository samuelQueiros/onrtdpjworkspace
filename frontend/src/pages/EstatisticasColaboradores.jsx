import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/estatisticas-colaboradores.css'
import ColaboradorSelect from '../components/estatisticasColaboradores/ColaboradorSelect'
import ResumoCards from '../components/estatisticasColaboradores/ResumoCards'
import DetalhesColaboradorSection from '../components/estatisticasColaboradores/DetalhesColaboradorSection'
import EvolucaoSalarialSection from '../components/estatisticasColaboradores/EvolucaoSalarialSection'
import ComposicaoRemuneracaoSection from '../components/estatisticasColaboradores/ComposicaoRemuneracaoSection'
import LinhaDoTempoSection from '../components/estatisticasColaboradores/LinhaDoTempoSection'
import { EmptyState, LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'

export default function EstatisticasColaboradores() {
  const toast = useToast()
  const [colaboradores, setColaboradores] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [ficha, setFicha] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingFicha, setLoadingFicha] = useState(false)

  useEffect(() => {
    api.listarUsuarios()
      .then(lista => {
        const ativos = lista.filter(colaborador => colaborador.ativo)
        setColaboradores(ativos)
        if (ativos.length === 1) setSelectedId(ativos[0].id)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const carregarFicha = useCallback(id => {
    setLoadingFicha(true)
    api.obterFichaAdmissional(id)
      .then(setFicha)
      .catch(error => toast.error(error.message))
      .finally(() => setLoadingFicha(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (selectedId) carregarFicha(selectedId)
    else setFicha(null)
  }, [selectedId, carregarFicha])

  if (loading) return <LoadingCard />

  const colaborador = colaboradores.find(item => item.id === selectedId)

  return (
    <>
      <PageHeader
        title="Estatísticas dos Colaboradores"
        subtitle="Dashboard do colaborador — base para o futuro Plano de Carreira."
      />

      <div className="card estatisticas-select-card">
        <ColaboradorSelect
          colaboradores={colaboradores}
          selectedId={selectedId}
          onChange={setSelectedId}
        />
      </div>

      {!colaborador && (
        <EmptyState
          title="Selecione um colaborador"
          text="Escolha um colaborador acima para ver o dashboard completo."
        />
      )}

      {colaborador && loadingFicha && <LoadingCard text="Carregando dados do colaborador..." />}

      {colaborador && !loadingFicha && (
        <div className="estatisticas-colaboradores-body">
          <ResumoCards user={colaborador} ficha={ficha} />

          <div className="card">
            <div className="card-body">
              <DetalhesColaboradorSection user={colaborador} ficha={ficha} />
            </div>
          </div>

          <div className="grid-2">
            <EvolucaoSalarialSection ficha={ficha} />
            <ComposicaoRemuneracaoSection ficha={ficha} />
          </div>

          <LinhaDoTempoSection user={colaborador} />
        </div>
      )}
    </>
  )
}
