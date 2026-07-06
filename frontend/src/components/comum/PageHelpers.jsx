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
