import { formatDate } from '../../utils/formatters'

export default function BlockedPeriodsPanel({ bloqueiosManuais, periodos }) {
  return (
    <aside className="card">
      <div className="card-header"><h2 className="card-title">Períodos indisponíveis</h2></div>
      <div className="card-body blocked-list">
        {bloqueiosManuais.length > 0 && (
          <>
            <div className="section-label">
              Bloqueios e Recessos
            </div>
            {bloqueiosManuais.map((bloqueio, index) => (
              <div className="blocked-item" key={`m-${index}`} style={{ borderLeftColor: bloqueio.tipo === 'recesso' ? 'var(--blue)' : 'var(--red)' }}>
                <strong>{bloqueio.motivo}</strong>
                <span>
                  {formatDate(bloqueio.data_inicio)} a {formatDate(bloqueio.data_fim)} - {bloqueio.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                </span>
              </div>
            ))}
            {periodos.length > 0 && <div className="divider" />}
          </>
        )}

        {periodos.length > 0 && (
          <>
            <div className="section-label">
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
  )
}
