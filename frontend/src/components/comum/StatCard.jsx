export default function StatCard({ icon, label, value, sub, children }) {
  return (
    <div className="stat-card">
      <div className="stat-icon-row">
        <div className="stat-label">{label}</div>
        {icon}
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-sub">{sub}</div>
      {children}
    </div>
  )
}
