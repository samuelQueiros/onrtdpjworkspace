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
  const [periodos, setPeriodos] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.disponibilidade().then(data => setPeriodos(data.periodos_bloqueados || [])).catch(() => setPeriodos([]))
  }, [])

  const dias = calcDays(dataInicio, dataFim)
  const bloqueado = dataInicio && dataFim && periodos.some(periodo => overlaps(dataInicio, dataFim, periodo))
  const saldoInsuficiente = dias > (user?.dias_restantes || 0)

  const submit = async event => {
    event.preventDefault()
    setError('')
    setSuccess('')
    if (!dias) return setError('Informe um periodo valido.')
    if (bloqueado) return setError('O periodo cruza datas bloqueadas por limite de colaboradores em ferias.')
    if (saldoInsuficiente) return setError('Voce nao possui saldo suficiente para esse periodo.')

    setSaving(true)
    try {
      await api.registrarFerias({ data_inicio: dataInicio, data_fim: dataFim })
      await refreshUser()
      setSuccess('Ferias registradas com sucesso.')
      setTimeout(() => navigate('/minhas-ferias'), 650)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader title="Solicitar Ferias" subtitle="Escolha um periodo e acompanhe o impacto no saldo antes de enviar." />

      <div className="grid-2 grid-2-wide-left">
        <form className="card form-card" onSubmit={submit}>
          <div className="card-header"><h2 className="card-title">Novo periodo</h2></div>
          <div className="card-body form-stack">
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Data de inicio</label>
                <input type="date" value={dataInicio} onChange={event => setDataInicio(event.target.value)} required />
                <small className="date-preview">Formato: {dataInicio ? formatDate(dataInicio) : 'DD/MM/AAAA'}</small>
              </div>
              <div className="form-group">
                <label>Data de fim</label>
                <input type="date" value={dataFim} onChange={event => setDataFim(event.target.value)} required />
                <small className="date-preview">Formato: {dataFim ? formatDate(dataFim) : 'DD/MM/AAAA'}</small>
              </div>
            </div>

            <div className="summary-panel">
              <div><span>Dias solicitados</span><strong>{dias || '-'}</strong></div>
              <div><span>Saldo atual</span><strong>{user?.dias_restantes}</strong></div>
              <div><span>Saldo apos envio</span><strong>{dias ? user?.dias_restantes - dias : '-'}</strong></div>
            </div>

            {bloqueado && <div className="alert alert-warning">Ha bloqueio de disponibilidade nesse intervalo.</div>}
            {saldoInsuficiente && <div className="alert alert-error">Saldo insuficiente para o periodo selecionado.</div>}

            <button className="btn btn-primary btn-lg" type="submit" disabled={saving || bloqueado || saldoInsuficiente || !dias}>
              {saving && <span className="inline-spinner" />}
              Registrar ferias
            </button>
          </div>
        </form>

        <aside className="card">
          <div className="card-header"><h2 className="card-title">Periodos bloqueados</h2></div>
          <div className="card-body blocked-list">
            {periodos.length ? periodos.map((periodo, index) => (
              <div className="blocked-item" key={index}>
                <strong>{formatDate(periodo.data_inicio)} a {formatDate(periodo.data_fim)}</strong>
                <span>Limite simultaneo atingido</span>
              </div>
            )) : <p className="muted">Nenhum periodo bloqueado no momento.</p>}
          </div>
        </aside>
      </div>
    </>
  )
}
