import { useEffect, useRef, useState } from 'react'
import '../styles/pages/solicitar-ferias.css'
import '../styles/pages/autorizacoes-equipamentos.css'
import { useNavigate } from 'react-router-dom'
import BlockedPeriodsPanel from '../components/solicitacaoFerias/BlockedPeriodsPanel'
import VacationRequestForm from '../components/solicitacaoFerias/VacationRequestForm'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { calcDays, formatDate } from '../utils/formatters'
import { overlaps, validarDataInicio } from '../utils/feriasValidation'
import { PageHeader } from '../components/comum/PageHelpers'
import AutorizacaoEquipamentoForm from '../components/autorizacoesEquipamentos/AutorizacaoEquipamentoForm'

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
  const [feriasOpen, setFeriasOpen] = useState(false)
  const [maquinaOpen, setMaquinaOpen] = useState(false)
  const submittingRef = useRef(false)

  useEffect(() => {
    api.disponibilidade()
      .then(data => {
        setPeriodos(data.periodos_bloqueados || [])
        setBloqueiosManuais(data.bloqueios_manuais || [])
      })
      .catch(error => {
        console.error('Falha ao carregar disponibilidade', error)
        setPeriodos([])
        setBloqueiosManuais([])
      })

    const anoAtual = new Date().getFullYear()
    Promise.all([
      api.feriados(anoAtual),
      api.feriados(anoAtual + 1),
    ])
      .then(([f1, f2]) => {
        setFeriadosSet(new Set([...f1, ...f2].map(feriado => feriado.data)))
      })
      .catch(error => console.error('Falha ao carregar feriados', error))
  }, [])

  const dias = calcDays(dataInicio, dataFim)
  const bloqueado = !feriasAcordo && dataInicio && dataFim && periodos.some(periodo => overlaps(dataInicio, dataFim, periodo))
  const bloqueioManual = dataInicio && dataFim && bloqueiosManuais.find(bloqueio => overlaps(dataInicio, dataFim, bloqueio))
  const saldoInsuficiente = !feriasAcordo && dias > (user?.dias_restantes || 0)
  const erroDatas = dataInicio && dataFim ? validarDataInicio(dataInicio, dataFim, feriadosSet) : null
  const podeSolicitar = !erroDatas && !bloqueioManual && (feriasAcordo || (!bloqueado && !saldoInsuficiente)) && !!dias

  const submit = async event => {
    event.preventDefault()
    if (submittingRef.current) return
    if (!dias) return toast.error('Informe um período válido.')
    if (erroDatas) return toast.error(erroDatas)
    if (bloqueioManual) {
      const tipo = bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'
      return toast.error(`O período selecionado está dentro de um ${tipo}: "${bloqueioManual.motivo}" (${formatDate(bloqueioManual.data_inicio)} a ${formatDate(bloqueioManual.data_fim)}).`)
    }
    if (bloqueado) return toast.error('O período cruza datas bloqueadas pelo limite de colaboradores em férias.')
    if (saldoInsuficiente) return toast.error('Você não possui saldo suficiente para esse período.')

    submittingRef.current = true
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
      if (res.status === 'pendente') window.dispatchEvent(new Event('approvals:changed'))
      setTimeout(() => navigate('/minhas-ferias'), 1200)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSaving(false)
      submittingRef.current = false
    }
  }

  return (
    <>
      <PageHeader title="Solicitações" subtitle="Escolha o tipo de solicitação que deseja enviar." />

      <div className="requests-stack">
        <section className="card request-disclosure">
          <button className="disclosure-button request-disclosure-button" type="button" aria-expanded={feriasOpen} aria-controls="solicitacao-ferias" onClick={() => setFeriasOpen(open => !open)}>
            <span>Solicitar férias</span>
            <span className="disclosure-chevron" aria-hidden="true">{feriasOpen ? '−' : '+'}</span>
          </button>
          {feriasOpen && <div id="solicitacao-ferias" className="request-disclosure-content grid-2 grid-2-wide-left">
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

            <BlockedPeriodsPanel bloqueiosManuais={bloqueiosManuais} periodos={periodos} />
          </div>}
        </section>

        <section className="card request-disclosure">
          <button className="disclosure-button request-disclosure-button" type="button" aria-expanded={maquinaOpen} aria-controls="autorizacao-maquina" onClick={() => setMaquinaOpen(open => !open)}>
            <span>Autorização de máquina</span>
            <span className="disclosure-chevron" aria-hidden="true">{maquinaOpen ? '−' : '+'}</span>
          </button>
          {maquinaOpen && <div id="autorizacao-maquina" className="request-placeholder">
            <AutorizacaoEquipamentoForm />
          </div>}
        </section>
      </div>
    </>
  )
}
