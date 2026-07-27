import { formatDate } from '../../utils/formatters'

export default function ResumoFeriasCards({ data, saldo }) {
  return (
    <>
      <section className="stat-grid stat-grid-3">
        <div className="stat-card">
          <div className="stat-label">Saldo disponível</div>
          <div className="stat-value">{saldo}</div>
          <div className="stat-sub">dias acumulados</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias usados</div>
          <div className="stat-value">{data?.dias_usados_total ?? 0}</div>
          <div className="stat-sub">no acumulado total</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Próxima concessão</div>
          <div className="stat-value text-sm">
            {data?.proxima_concessao_ferias ? formatDate(data.proxima_concessao_ferias) : '-'}
          </div>
          <div className="stat-sub">crédito automático da cota anual</div>
        </div>
      </section>
    </>
  )
}
