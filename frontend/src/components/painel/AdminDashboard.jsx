import AdminActionsAndAlerts from './AdminActionsAndAlerts'
import AdminStats from './AdminStats'
import AdminVacationOverview from './AdminVacationOverview'

export default function AdminDashboard({ dash, pendentes }) {
  const alertas = dash.alertas_contabilidade || []

  return (
    <div className="admin-dashboard-sections">
      <AdminStats dash={dash} pendentes={pendentes} />
      <AdminVacationOverview
        pessoasEmFerias={dash.pessoas_em_ferias || []}
        proximasFerias={dash.proximas_ferias || []}
      />
      <AdminActionsAndAlerts alertas={alertas} pendentes={pendentes} />
    </div>
  )
}
