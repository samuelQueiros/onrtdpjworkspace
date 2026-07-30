import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { formatCurrency } from '../DetailFields'
import { formatDate } from '../../../utils/formatters'
import { EmptyState } from '../PageHelpers'

const LINE_COLOR = 'var(--green)'

function EndLabel({ x, y, index, dados, value }) {
  if (index !== dados.length - 1) return null
  return (
    <text x={x} y={y - 14} textAnchor="middle" className="chart-end-label">
      {formatCurrency(value)}
    </text>
  )
}

function TooltipContent({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <strong>{formatCurrency(payload[0].value)}</strong>
      <span>{formatDate(label)}</span>
    </div>
  )
}

export default function SalaryLineChart({ data }) {
  if (!data?.length) {
    return <EmptyState title="Sem dados salariais" text="Nenhum salário cadastrado na ficha admissional." />
  }

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data} margin={{ top: 24, right: 16, left: 8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="var(--border)" strokeDasharray="0" />
          <XAxis
            dataKey="data"
            tickFormatter={formatDate}
            tick={{ fill: 'var(--muted)', fontSize: 11 }}
            axisLine={{ stroke: 'var(--border)' }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={value => formatCurrency(value)}
            tick={{ fill: 'var(--muted)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={80}
          />
          <Tooltip content={<TooltipContent />} cursor={{ stroke: 'var(--border)' }} />
          <Area
            type="monotone"
            dataKey="valor"
            stroke={LINE_COLOR}
            strokeWidth={2}
            fill={LINE_COLOR}
            fillOpacity={0.1}
            dot={{ r: 4, fill: LINE_COLOR, stroke: 'var(--card)', strokeWidth: 2 }}
            activeDot={{ r: 5, fill: LINE_COLOR, stroke: 'var(--card)', strokeWidth: 2 }}
            label={props => <EndLabel {...props} dados={data} />}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      {data.length === 1 && (
        <p className="muted chart-hint">Sem histórico suficiente — exibindo apenas o valor atual.</p>
      )}
    </div>
  )
}
