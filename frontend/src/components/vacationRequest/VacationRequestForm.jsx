import { formatDate } from '../../utils/formatters'

export default function VacationRequestForm({
  bloqueado,
  bloqueioManual,
  dataFim,
  dataInicio,
  dias,
  erroDatas,
  error,
  feriasAcordo,
  onDataFimChange,
  onDataInicioChange,
  onFeriasAcordoChange,
  onSubmit,
  podeSolicitar,
  saldoInsuficiente,
  saving,
  success,
  user,
}) {
  return (
    <form className="card form-card" onSubmit={onSubmit}>
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
              onChange={event => onDataInicioChange(event.target.value)}
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
              onChange={event => onDataFimChange(event.target.value)}
              required
            />
            <small className="date-preview">
              Formato: {dataFim ? formatDate(dataFim) : 'DD/MM/AAAA'}
            </small>
          </div>
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              hidden
              type="checkbox"
              checked={feriasAcordo}
              onChange={event => onFeriasAcordoChange(event.target.checked)}
            />
            <span hidden>Férias por acordo (não desconta saldo)</span>
          </label>
        </div>

        <div className="summary-panel">
          <div><span>Dias solicitados</span><strong>{dias || '-'}</strong></div>
          <div><span>Saldo atual</span><strong>{user?.dias_restantes}</strong></div>
          <div>
            <span>Saldo após envio</span>
            <strong>{feriasAcordo ? user?.dias_restantes : (dias ? (user?.dias_restantes - dias) : '-')}</strong>
          </div>
        </div>

        {erroDatas && (
          <div className="alert alert-error">{erroDatas}</div>
        )}
        {!erroDatas && bloqueioManual && (
          <div className="alert alert-error">
            Período bloqueado: {bloqueioManual.tipo === 'recesso' ? 'recesso' : 'bloqueio'} - "{bloqueioManual.motivo}"
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
  )
}
