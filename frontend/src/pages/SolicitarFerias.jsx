import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BlockedPeriodsPanel from '../components/vacationRequest/BlockedPeriodsPanel'
import VacationRequestForm from '../components/vacationRequest/VacationRequestForm'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { calcDays, formatDate } from '../utils/formatters'
import { overlaps, validarDataInicio } from '../utils/feriasValidation'
import { PageHeader } from './_helpers'

export default function SolicitarFerias() {
  const navigate = useNavigate()
  const { user, refreshUser } = useAuth()
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [feriasAcordo, setFeriasAcordo] = useState(false)
  const [periodos, setPeriodos] = useState([])
  const [bloqueiosManuais, setBloqueiosManuais] = useState([])
  const [feriadosSet, setFeriadosSet] = useState(new Set())
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
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
    setError('')
    setSuccess('')
    if (!dias) return setError('Informe um período válido.')
    if (erroDatas) return setError(erroDatas)
    if (bloqueioManual) {
      const tipo = bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'
      return setError(`O período selecionado está dentro de um ${tipo}: "${bloqueioManual.motivo}" (${formatDate(bloqueioManual.data_inicio)} a ${formatDate(bloqueioManual.data_fim)}).`)
    }
    if (bloqueado) return setError('O período cruza datas bloqueadas pelo limite de colaboradores em férias.')
    if (saldoInsuficiente) return setError('Você não possui saldo suficiente para esse período.')

    setSaving(true)
    try {
      const res = await api.registrarFerias({
        data_inicio: dataInicio,
        data_fim: dataFim,
        ferias_acordo: feriasAcordo,
      })
      await refreshUser()
      setSuccess(res.status === 'pendente'
        ? 'Solicitação enviada! Aguarde a aprovação do administrador.'
        : 'Férias registradas com sucesso.')
      setTimeout(() => navigate('/minhas-ferias'), 1200)
    } catch (err) {
      setError(err.message)
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
          error={error}
          feriasAcordo={feriasAcordo}
          onDataFimChange={setDataFim}
          onDataInicioChange={setDataInicio}
          onFeriasAcordoChange={setFeriasAcordo}
          onSubmit={submit}
          podeSolicitar={podeSolicitar}
          saldoInsuficiente={saldoInsuficiente}
          saving={saving}
          success={success}
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
