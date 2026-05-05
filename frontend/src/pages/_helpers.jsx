export function PageHeader({ title, subtitle, action }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function StatusBadge({ children, tone = 'gray' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>
}

export function LoadingCard({ text = 'Carregando dados...' }) {
  return (
    <div className="card">
      <div className="empty">
        <div className="spinner" />
        <p>{text}</p>
      </div>
    </div>
  )
}

export function EmptyState({ title, text }) {
  return (
    <div className="empty">
      <div className="empty-icon">--</div>
      <h3>{title}</h3>
      <p>{text}</p>
    </div>
  )
}

export function formatDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return '-'
  return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  const data = formatDate(date.toISOString().slice(0, 10))
  const hora = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return `${data} ${hora}`
}

export function calcDays(start, end) {
  if (!start || !end) return 0
  const a = new Date(`${start}T12:00:00`)
  const b = new Date(`${end}T12:00:00`)
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime()) || b < a) return 0
  return Math.floor((b - a) / 86400000) + 1
}
