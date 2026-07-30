import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { formatCurrency } from '../DetailFields'
import { EmptyState } from '../PageHelpers'

function TooltipContent({ active, payload }) {
  if (!active || !payload?.length) return null
  const item = payload[0]
  return (
    <div className="chart-tooltip">
      <strong>{formatCurrency(item.value)}</strong>
      <span>{item.name}</span>
    </div>
  )
}

function Legend({ data, total }) {
  return (
    <ul className="chart-legend">
      {data.map(item => (
        <li key={item.nome}>
          <span className="chart-legend-swatch" style={{ background: item.cor }} aria-hidden="true" />
          <span className="chart-legend-label">{item.nome}</span>
          <span className="chart-legend-value">
            {formatCurrency(item.valor)}
            {total > 0 && <span className="muted"> · {Math.round((item.valor / total) * 100)}%</span>}
          </span>
        </li>
      ))}
    </ul>
  )
}

export default function CompositionDonutChart({ data }) {
  const dadosValidos = (data || []).filter(item => item.valor > 0)
  const total = dadosValidos.reduce((soma, item) => soma + item.valor, 0)

  if (!dadosValidos.length) {
    return <EmptyState title="Sem dados de remuneração" text="Cadastre o salário na ficha admissional para ver a composição." />
  }

  return (
    <div className="chart-wrap chart-wrap-donut">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Tooltip content={<TooltipContent />} />
          <Pie
            data={dadosValidos}
            dataKey="valor"
            nameKey="nome"
            innerRadius="62%"
            outerRadius="90%"
            paddingAngle={dadosValidos.length > 1 ? 3 : 0}
            stroke="var(--card)"
            strokeWidth={2}
            isAnimationActive={false}
          >
            {dadosValidos.map(item => <Cell key={item.nome} fill={item.cor} />)}
          </Pie>
          <text x="50%" y="47%" textAnchor="middle" className="chart-donut-total-label">Total</text>
          <text x="50%" y="58%" textAnchor="middle" className="chart-donut-total-value">
            {formatCurrency(total)}
          </text>
        </PieChart>
      </ResponsiveContainer>
      <Legend data={dadosValidos} total={total} />
    </div>
  )
}
