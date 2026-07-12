import { useEffect, useState } from 'react'
import '../styles/pages/solicitar-ferias.css'
import { useNavigate } from 'react-router-dom'
import BlockedPeriodsPanel from '../components/solicitacaoFerias/BlockedPeriodsPanel'
import VacationRequestForm from '../components/solicitacaoFerias/VacationRequestForm'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { calcDays, formatDate } from '../utils/formatters'
import { overlaps, validarDataInicio } from '../utils/feriasValidation'
import { PageHeader } from '../components/comum/PageHelpers'

export default function SolicitarFerias() {
  const navigate = useNavigate()
  const { user, refreshUser } = useAuth()
  const toast = useToast()
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [feriasAcordo, setFeriasAcordo] = useState(false)
  const [periodos, setPeriodos] = useState([])
  const [bloqueiosManuais, setBloqueiosManuais] = useState([])
  const [feriadosSet, setFeriadosSet] = useState(new Set())
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.disponibilidade()
      .then(data => {
        setPeriodos(data.periodos_bloqueados || [])
        setBloqueiosManuais(data.bloqueios_manuais || [])
      })
      .catch(() => { setPeriodos([]); setBloqueiosManuais([]) })

    const anoAtual = new Date().getFullYear()
    Promise.all([
      api.feriados(anoAtual),
      api.feriados(anoAtual + 1),
    ])
      .then(([f1, f2]) => {
        setFeriadosSet(new Set([...f1, ...f2].map(feriado => feriado.data)))
      })
      .catch(() => {})
  }, [])

  const dias = calcDays(dataInicio, dataFim)
  const bloqueado = !feriasAcordo && dataInicio && dataFim && periodos.some(periodo => overlaps(dataInicio, dataFim, periodo))
  const bloqueioManual = dataInicio && dataFim && bloqueiosManuais.find(bloqueio => overlaps(dataInicio, dataFim, bloqueio))
  const saldoInsuficiente = !feriasAcordo && dias > (user?.dias_restantes || 0)
  const erroDatas = dataInicio && dataFim ? validarDataInicio(dataInicio, dataFim, feriadosSet) : null
  const podeSolicitar = !erroDatas && !bloqueioManual && (feriasAcordo || (!bloqueado && !saldoInsuficiente)) && !!dias

  const submit = async event => {
    event.preventDefault()
    if (!dias) return toast.error('Informe um período válido.')
    if (erroDatas) return toast.error(erroDatas)
    if (bloqueioManual) {
      const tipo = bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'
      return toast.error(`O período selecionado está dentro de um ${tipo}: "${bloqueioManual.motivo}" (${formatDate(bloqueioManual.data_inicio)} a ${formatDate(bloqueioManual.data_fim)}).`)
    }
    if (bloqueado) return toast.error('O período cruza datas bloqueadas pelo limite de colaboradores em férias.')
    if (saldoInsuficiente) return toast.error('Você não possui saldo suficiente para esse período.')

    setSaving(true)
    try {
      const res = await api.registrarFerias({
        data_inicio: dataInicio,
        data_fim: dataFim,
        ferias_acordo: feriasAcordo,
      })
      await refreshUser()
      toast.success(res.status === 'pendente'
        ? 'Solicitação enviada! Aguarde a aprovação do administrador.'
        : 'Férias registradas com sucesso.')
      setTimeout(() => navigate('/minhas-ferias'), 1200)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader title="Solicitar Férias" subtitle="Escolha um período e acompanhe o impacto no saldo antes de enviar." />

      <div className="grid-2 grid-2-wide-left">
        <VacationRequestForm
          bloqueado={bloqueado}
          bloqueioManual={bloqueioManual}
          dataFim={dataFim}
          dataInicio={dataInicio}
          dias={dias}
          erroDatas={erroDatas}
          feriasAcordo={feriasAcordo}
          onDataFimChange={setDataFim}
          onDataInicioChange={setDataInicio}
          onFeriasAcordoChange={setFeriasAcordo}
          onSubmit={submit}
          podeSolicitar={podeSolicitar}
          saldoInsuficiente={saldoInsuficiente}
          saving={saving}
          user={user}
        />

        <BlockedPeriodsPanel
          bloqueiosManuais={bloqueiosManuais}
          periodos={periodos}
        />
      </div>
    </>
  )
}
