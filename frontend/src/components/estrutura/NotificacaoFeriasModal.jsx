import { formatDate } from '../../utils/formatters'
import { copiarModeloEmailFerias } from '../../utils/emailTemplates'

const KICKER_POR_TIPO = {
  ferias_5dias: 'Aviso de férias em 5 dias',
  ferias_4dias: 'Lembrete urgente — férias próximas',
}

export default function NotificacaoFeriasModal({ alerta, total, onCopiar, onFechar }) {
  const kicker = KICKER_POR_TIPO[alerta.tipo] || 'Aviso de férias'

  const copiar = async () => {
    try {
      await copiarModeloEmailFerias(alerta)
      onCopiar(true)
    } catch {
      onCopiar(false)
    }
  }

  return (
    <div className="modal-overlay ferias-alerta-overlay" role="presentation">
      <section
        className="modal ferias-alerta-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="ferias-alerta-title"
      >
        <div className="modal-header">
          <div>
            <p className="ferias-alerta-kicker">{kicker}</p>
            <h3 id="ferias-alerta-title">{alerta.ferias_usuario}</h3>
          </div>
          {total > 1 && <span className="ferias-alerta-contador">+{total - 1} outro(s)</span>}
        </div>
        <div className="modal-body">
          <p>
            <strong>{alerta.ferias_usuario}</strong> entra em férias em{' '}
            <strong>{formatDate(alerta.ferias_data_inicio)}</strong>, com retorno previsto em{' '}
            <strong>{formatDate(alerta.retorno_trabalho)}</strong>.
          </p>
          <p className="muted">
            Período: {formatDate(alerta.ferias_data_inicio)} a {formatDate(alerta.ferias_data_fim)}
            {alerta.ferias_dias_usados ? ` (${alerta.ferias_dias_usados} dia(s))` : ''}.
          </p>
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={onFechar}>Fechar aviso</button>
          <button className="btn btn-primary" type="button" onClick={copiar}>Copiar modelo de e-mail</button>
        </div>
      </section>
    </div>
  )
}
