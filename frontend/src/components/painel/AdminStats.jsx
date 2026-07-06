import { Link } from 'react-router-dom'
import { DashboardIcon as Icon } from './DashboardIcons'

function StatCard({ icon, label, value, sub, children }) {
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

export default function AdminStats({ dash }) {
  return (
    <section className="stat-grid">
      <StatCard
        icon={<div className="stat-icon-box navy">{Icon.users}</div>}
        label="Colaboradores"
        value={dash.total_colaboradores}
        sub={`${dash.total_departamentos} departamento(s)`}
      />
      <StatCard
        icon={<div className="stat-icon-box green">{Icon.check}</div>}
        label="Aprovadas"
        value={dash.total_ferias_aprovadas}
        sub="períodos aprovados"
      />
      <StatCard
        icon={<div className="stat-icon-box amber">{Icon.clock}</div>}
        label="Pendentes"
        value={dash.total_ferias_pendentes}
        sub="aguardando revisão"
      >
        {dash.total_ferias_pendentes > 0 && (
          <div className="mt-8">
            <Link className="btn btn-outline btn-sm" to="/aprovacoes">Revisar →</Link>
          </div>
        )}
      </StatCard>
      <StatCard
        icon={<div className="stat-icon-box red">{Icon.x}</div>}
        label="Rejeitadas"
        value={dash.total_ferias_rejeitadas}
        sub="solicitações negadas"
      />
    </section>
  )
}
