import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import { PageHeader, calcDays, formatDate } from './_helpers'

function overlaps(start, end, period) {
  return start <= period.data_fim && end >= period.data_inicio
}

export default function SolicitarFerias() {
  const navigate = useNavigate()
  const { user, refreshUser } = useAuth()
  const [dataInicio, setDataInicio] = useState('')
  const [dataFim, setDataFim] = useState('')
  const [feriasAcordo, setFeriasAcordo] = useState(false)
  const [periodos, setPeriodos] = useState([])
  const [bloqueiosManuais, setBloqueiosManuais] = useState([])
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
  }, [])

  const dias = calcDays(dataInicio, dataFim)
  const bloqueado = !feriasAcordo && dataInicio && dataFim && periodos.some(p => overlaps(dataInicio, dataFim, p))
  const bloqueioManual = dataInicio && dataFim && bloqueiosManuais.find(b => overlaps(dataInicio, dataFim, b))
  const saldoInsuficiente = !feriasAcordo && dias > (user?.dias_restantes || 0)

  const submit = async event => {
    event.preventDefault()
    setError('')
    setSuccess('')
    if (!dias) return setError('Informe um período válido.')
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

            {bloqueioManual && (
              <div className="alert alert-error">
                Período bloqueado: {bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'} — "{bloqueioManual.motivo}"
              </div>
            )}
            {bloqueado && !bloqueioManual && (
              <div className="alert alert-warning">Há bloqueio de disponibilidade nesse intervalo.</div>
            )}
            {saldoInsuficiente && (
              <div className="alert alert-error">Saldo insuficiente para o período selecionado.</div>
            )}

            <button
              className="btn btn-primary btn-lg"
              type="submit"
              disabled={saving || bloqueioManual || (!feriasAcordo && (bloqueado || saldoInsuficiente)) || !dias}
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
