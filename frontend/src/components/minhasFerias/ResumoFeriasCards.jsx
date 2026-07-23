import DiasVencidosAlert from '../comum/DiasVencidosAlert'
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
          <div className="stat-label">Ciclo atual</div>
          <div className="stat-value text-sm">
            {data?.ciclo_inicio ? formatDate(data.ciclo_inicio) : '-'} a {data?.ciclo_fim ? formatDate(data.ciclo_fim) : '-'}
          </div>
          <div className="stat-sub">período aquisitivo em curso</div>
        </div>
      </section>

      <DiasVencidosAlert vencidas={data?.dias_vencidos} />
    </>
  )
}
