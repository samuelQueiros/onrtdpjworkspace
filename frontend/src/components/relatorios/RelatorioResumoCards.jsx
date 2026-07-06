export default function RelatorioResumoCards({ colaboradores, totalColaboradores }) {
  const totalDias = colaboradores.reduce((sum, colaborador) => sum + colaborador.dias_totais, 0)
  const usados = colaboradores.reduce((sum, colaborador) => sum + colaborador.dias_usados, 0)
  const pendentes = colaboradores.reduce((sum, colaborador) => sum + colaborador.ferias_pendentes.length, 0)

  return (
    <section className="stat-grid">
      <div className="stat-card">
        <div className="stat-label">Colaboradores</div>
        <div className="stat-value">{totalColaboradores}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Dias totais</div>
        <div className="stat-value">{totalDias}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Dias usados</div>
        <div className="stat-value">{usados}</div>
      </div>
      <div className="stat-card">
        <div className="stat-label">Pendentes</div>
        <div className="stat-value">{pendentes}</div>
        <div className="stat-sub">aguardando aprovação</div>
      </div>
    </section>
  )
}
