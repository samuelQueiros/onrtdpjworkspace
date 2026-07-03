import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { PageHeader, calcDays, formatDate } from './_helpers'

const NOMES_DIA = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']

function overlaps(start, end, period) {
  return start <= period.data_fim && end >= period.data_inicio
}

function parseDate(str) {
  if (!str) return null
  const [y, m, d] = str.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function primeiroDiaDescansoNaSemana(ref, feriadosSet) {
  // Acha a segunda-feira da semana de `ref`
  const seg = new Date(ref)
  seg.setDate(ref.getDate() - ref.getDay() + (ref.getDay() === 0 ? -6 : 1))
  for (let delta = 0; delta < 5; delta++) {
    const dia = new Date(seg)
    dia.setDate(seg.getDate() + delta)
    const iso = dia.toISOString().split('T')[0]
    if (feriadosSet.has(iso)) return delta // 0=seg..4=sex
  }
  return 5 // sábado por padrão
}

function validarDataInicio(dataInicio, dataFim, feriadosSet) {
  const hoje = new Date()
  hoje.setHours(0, 0, 0, 0)

  const inicio = parseDate(dataInicio)
  const fim = parseDate(dataFim)

  if (!inicio || !fim) return null

  if (fim < inicio) {
    return 'A data de fim não pode ser anterior à data de início.'
  }

  if (inicio < hoje) {
    return 'A data de início não pode ser anterior a hoje.'
  }

  // getDay(): 0=dom, 1=seg, ..., 6=sab → converte para 0=seg..6=dom
  const getDow = d => (d.getDay() + 6) % 7

  const dia = getDow(inicio)

  if (dia >= 5) {
    return `Férias não podem iniciar em ${NOMES_DIA[dia]} (dia de descanso).`
  }

  const limite = primeiroDiaDescansoNaSemana(inicio, feriadosSet)
  const bloqueados = new Set(
    [limite - 2, limite - 1, limite].filter(d => d >= 0 && d <= 4)
  )

  if (bloqueados.has(dia)) {
    if (limite < 5) {
      // Encontra a data do feriado
      const seg = new Date(inicio)
      seg.setDate(inicio.getDate() - getDow(inicio))
      const feriadoDia = new Date(seg)
      feriadoDia.setDate(seg.getDate() + limite)
      const feriadoStr = feriadoDia.toLocaleDateString('pt-BR')
      const motivo = `há um feriado em ${NOMES_DIA[limite]} (${feriadoStr}) nesta semana, antecipando o período de descanso`
      const permitidos = [0, 1, 2, 3, 4].filter(d => !bloqueados.has(d)).map(d => NOMES_DIA[d])
      const sufixo = permitidos.length
        ? ` Dias permitidos nesta semana: ${permitidos.join(', ')}.`
        : ' Não há dia de início permitido nesta semana.'
      return `Férias não podem iniciar em ${NOMES_DIA[dia]}: ${motivo}.${sufixo}`
    } else {
      const permitidos = [0, 1, 2, 3, 4].filter(d => !bloqueados.has(d)).map(d => NOMES_DIA[d])
      return `Férias não podem iniciar em ${NOMES_DIA[dia]}: está a menos de 48 horas do descanso semanal (sábado). Dias permitidos: ${permitidos.join(', ')}.`
    }
  }

  return null
}

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
        setFeriadosSet(new Set([...f1, ...f2].map(f => f.data)))
      })
      .catch(() => {})
  }, [])

  const dias = calcDays(dataInicio, dataFim)
  const bloqueado = !feriasAcordo && dataInicio && dataFim && periodos.some(p => overlaps(dataInicio, dataFim, p))
  const bloqueioManual = dataInicio && dataFim && bloqueiosManuais.find(b => overlaps(dataInicio, dataFim, b))
  const saldoInsuficiente = !feriasAcordo && dias > (user?.dias_restantes || 0)
  const erroDatas = dataInicio && dataFim ? validarDataInicio(dataInicio, dataFim, feriadosSet) : null

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
      const msg = res.status === 'pendente'
        ? 'Solicitação enviada! Aguarde a aprovação do administrador.'
        : 'Férias registradas com sucesso.'
      setSuccess(msg)
      setTimeout(() => navigate('/minhas-ferias'), 1200)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  const podeSolicitar = !erroDatas && !bloqueioManual && (feriasAcordo || (!bloqueado && !saldoInsuficiente)) && !!dias

  return (
    <>
      <PageHeader title="Solicitar Férias" subtitle="Escolha um período e acompanhe o impacto no saldo antes de enviar." />

      <div className="grid-2 grid-2-wide-left">
        <form className="card form-card" onSubmit={submit}>
          <div className="card-header"><h2 className="card-title">Novo período</h2></div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Data de início</label>
                <input
                  type="date"
                  value={dataInicio}
                  onChange={e => setDataInicio(e.target.value)}
                  required
                />
                <small className="date-preview">
                  Formato: {dataInicio ? formatDate(dataInicio) : 'DD/MM/AAAA'}
                </small>
              </div>
              <div className="form-group">
                <label>Data de fim</label>
                <input
                  type="date"
                  value={dataFim}
                  onChange={e => setDataFim(e.target.value)}
                  required
                />
                <small className="date-preview">
                  Formato: {dataFim ? formatDate(dataFim) : 'DD/MM/AAAA'}
                </small>
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input hidden
                  type="checkbox"
                  checked={feriasAcordo}
                  onChange={e => setFeriasAcordo(e.target.checked)}
                />
                <span hidden>Férias por acordo (não desconta saldo)</span>
              </label>
            </div>

            <div className="summary-panel">
              <div><span>Dias solicitados</span><strong>{dias || '—'}</strong></div>
              <div><span>Saldo atual</span><strong>{user?.dias_restantes}</strong></div>
              <div>
                <span>Saldo após envio</span>
                <strong>{feriasAcordo ? user?.dias_restantes : (dias ? (user?.dias_restantes - dias) : '—')}</strong>
              </div>
            </div>

            {erroDatas && (
              <div className="alert alert-error">{erroDatas}</div>
            )}
            {!erroDatas && bloqueioManual && (
              <div className="alert alert-error">
                Período bloqueado: {bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'} — "{bloqueioManual.motivo}"
              </div>
            )}
            {!erroDatas && bloqueado && !bloqueioManual && (
              <div className="alert alert-warning">Há bloqueio de disponibilidade nesse intervalo.</div>
            )}
            {!erroDatas && saldoInsuficiente && (
              <div className="alert alert-error">Saldo insuficiente para o período selecionado.</div>
            )}

            <button
              className="btn btn-primary btn-lg"
              type="submit"
              disabled={saving || !podeSolicitar}
            >
              {saving && <span className="inline-spinner" />}
              Enviar solicitação
            </button>
          </div>
        </form>

        <aside className="card">
          <div className="card-header"><h2 className="card-title">Períodos indisponíveis</h2></div>
          <div className="card-body blocked-list">
            {bloqueiosManuais.length > 0 && (
              <>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.5px', color: 'var(--muted)', marginBottom: 4 }}>
                  Bloqueios e Recessos
                </div>
                {bloqueiosManuais.map((b, i) => (
                  <div className="blocked-item" key={`m-${i}`} style={{ borderLeftColor: b.tipo === 'recesso' ? 'var(--blue)' : 'var(--red)' }}>
                    <strong>{b.motivo}</strong>
                    <span>{formatDate(b.data_inicio)} a {formatDate(b.data_fim)} — {b.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}</span>
                  </div>
                ))}
                {periodos.length > 0 && <div className="divider" />}
              </>
            )}
            {periodos.length > 0 && (
              <>
                <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.5px', color: 'var(--muted)', marginBottom: 4 }}>
                  Limite de equipe atingido
                </div>
                {periodos.map((periodo, index) => (
                  <div className="blocked-item" key={index}>
                    <strong>{formatDate(periodo.data_inicio)} a {formatDate(periodo.data_fim)}</strong>
                    <span>Limite simultâneo atingido</span>
                  </div>
                ))}
              </>
            )}
            {bloqueiosManuais.length === 0 && periodos.length === 0 && (
              <p className="muted">Nenhum período bloqueado no momento.</p>
            )}
          </div>
        </aside>
      </div>
    </>
  )
}
