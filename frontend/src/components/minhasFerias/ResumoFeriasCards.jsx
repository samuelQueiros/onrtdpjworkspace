import { formatDate } from '../../utils/formatters'

export default function ResumoFeriasCards({ data, saldo }) {
  return (
    <section className="stat-grid stat-grid-3">
      <div className="stat-card">
        <div className="stat-label">Saldo disponível</div>
        <div className="stat-value">{saldo}</div>
        <div className="stat-sub">dias no ciclo atual</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Ciclo início</div>
        <div className="stat-value text-sm">{data?.ciclo_inicio ? formatDate(data.ciclo_inicio) : '-'}</div>
        <div className="stat-sub">início do período anual</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Ciclo fim</div>
        <div className="stat-value text-sm">{data?.ciclo_fim ? formatDate(data.ciclo_fim) : '-'}</div>
        <div className="stat-sub">encerramento do ciclo</div>
      </div>
    </section>
  )
}
