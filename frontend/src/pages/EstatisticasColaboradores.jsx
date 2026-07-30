import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/estatisticas-colaboradores.css'
import ColaboradorSelect from '../components/estatisticasColaboradores/ColaboradorSelect'
import ResumoCards from '../components/estatisticasColaboradores/ResumoCards'
import DetalhesColaboradorSection from '../components/estatisticasColaboradores/DetalhesColaboradorSection'
import EditarDadosColaboradorForm from '../components/estatisticasColaboradores/EditarDadosColaboradorForm'
import EvolucaoSalarialSection from '../components/estatisticasColaboradores/EvolucaoSalarialSection'
import ComposicaoRemuneracaoSection from '../components/estatisticasColaboradores/ComposicaoRemuneracaoSection'
import LinhaDoTempoSection from '../components/estatisticasColaboradores/LinhaDoTempoSection'
import { EmptyState, LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'

export default function EstatisticasColaboradores() {
  const toast = useToast()
  const [colaboradores, setColaboradores] = useState([])
  const [cargos, setCargos] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [ficha, setFicha] = useState(null)
  const [historicoSalarial, setHistoricoSalarial] = useState([])
  const [historicoFuncional, setHistoricoFuncional] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadingFicha, setLoadingFicha] = useState(false)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    Promise.all([api.listarUsuarios(), api.listarCargos(), api.listarDepartamentos()])
      .then(([lista, listaCargos, listaDepartamentos]) => {
        const ativos = lista.filter(colaborador => colaborador.ativo)
        setColaboradores(ativos)
        setCargos(listaCargos)
        setDepartamentos(listaDepartamentos)
        if (ativos.length === 1) setSelectedId(ativos[0].id)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const carregarFicha = useCallback(id => {
    setLoadingFicha(true)
    Promise.all([
      api.obterFichaAdmissional(id),
      api.historicoSalarial(id),
      api.historicoFuncional(id),
    ])
      .then(([dadosFicha, dadosHistoricoSalarial, dadosHistoricoFuncional]) => {
        setFicha(dadosFicha)
        setHistoricoSalarial(dadosHistoricoSalarial)
        setHistoricoFuncional(dadosHistoricoFuncional)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoadingFicha(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    setEditing(false)
    if (selectedId) {
      carregarFicha(selectedId)
    } else {
      setFicha(null)
      setHistoricoSalarial([])
      setHistoricoFuncional([])
    }
  }, [selectedId, carregarFicha])

  const salvarEdicao = async ({ userPayload, fichaPayload }) => {
    if (!selectedId) return
    setSaving(true)
    try {
      const [colaboradorAtualizado] = await Promise.all([
        api.editarUsuario(selectedId, userPayload),
        api.editarFichaAdmissional(selectedId, fichaPayload),
      ])
      setColaboradores(lista => lista.map(item => (item.id === selectedId ? colaboradorAtualizado : item)))
      await carregarFicha(selectedId)
      setEditing(false)
      toast.success('Dados do colaborador atualizados com sucesso.')
    } catch (error) {
      toast.error(error.message)
      throw error
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingCard />

  const colaborador = colaboradores.find(item => item.id === selectedId)

  return (
    <>
      <PageHeader
        title="Estatísticas dos Colaboradores"
        subtitle="Dashboard do colaborador — base para o futuro Plano de Carreira."
        action={colaborador && !loadingFicha && (
          <button className="btn btn-outline" type="button" onClick={() => setEditing(open => !open)}>
            {editing ? 'Cancelar edição' : 'Editar dados'}
          </button>
        )}
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
          {editing && (
            <EditarDadosColaboradorForm
              user={colaborador}
              ficha={ficha}
              cargos={cargos}
              departamentos={departamentos}
              saving={saving}
              onSave={salvarEdicao}
              onCancel={() => setEditing(false)}
            />
          )}

          <ResumoCards user={colaborador} ficha={ficha} />

          <div className="card">
            <div className="card-body">
              <DetalhesColaboradorSection user={colaborador} ficha={ficha} />
            </div>
          </div>

          <div className="grid-2">
            <EvolucaoSalarialSection ficha={ficha} historico={historicoSalarial} />
            <ComposicaoRemuneracaoSection ficha={ficha} />
          </div>

          <LinhaDoTempoSection user={colaborador} historicoSalarial={historicoSalarial} historicoFuncional={historicoFuncional} />
        </div>
      )}
    </>
  )
}
