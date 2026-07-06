import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import AvisoCard from './AvisoCard'

export default function UserDashboard({ user, ferias, avisos }) {
  const usados = user ? user.dias_totais - user.dias_restantes : 0

  const proximas = useMemo(() => {
    const today = new Date()
    const lista = Array.isArray(ferias) ? ferias : (ferias?.ferias || [])
    return lista
      .filter(item => item.status === 'aprovada' && new Date(`${item.data_fim}T23:59:59`) >= today)
      .sort((a, b) => String(a.data_inicio).localeCompare(String(b.data_inicio)))
      .slice(0, 4)
  }, [ferias])

  return (
    <>
      <section className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Dias restantes</div>
          <div className="stat-value">{user?.dias_restantes}</div>
          <div className="stat-sub">de {user?.dias_totais} dias no ciclo</div>
          <div className="progress-track">
            <div
              className="progress-fill green"
              style={{ width: `${Math.max(0, (user?.dias_restantes / user?.dias_totais) * 100)}%` }}
            />
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias usados</div>
          <div className="stat-value">{usados}</div>
          <div className="stat-sub">dias já registrados no ciclo</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Meus períodos</div>
          <div className="stat-value">{Array.isArray(ferias) ? ferias.length : (ferias?.ferias?.length ?? 0)}</div>
          <div className="stat-sub">solicitações no sistema</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avisos ativos</div>
          <div className="stat-value">{avisos.length}</div>
          <div className="stat-sub">no mural</div>
        </div>
      </section>

      <div className="grid-2">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Próximas férias</h2></div>
          <div className="table-wrap">
            {proximas.length ? (
              <table>
                <thead><tr><th>Início</th><th>Fim</th><th>Dias</th><th>Status</th></tr></thead>
                <tbody>
                  {proximas.map(item => (
                    <tr key={item.id}>
                      <td>{formatDate(item.data_inicio)}</td>
                      <td>{formatDate(item.data_fim)}</td>
                      <td>{item.dias_usados}</td>
                      <td><StatusBadge tone="green">Aprovada</StatusBadge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <EmptyState title="Nenhum período futuro" text="Quando você registrar férias aprovadas, elas aparecerão aqui." />
            )}
          </div>
        </section>

        <section className="card">
          <div className="card-header"><h2 className="card-title">Atalhos rápidos</h2></div>
          <div className="card-body quick-actions">
            <Link className="quick-action" to="/solicitar">
              <strong>Solicitar férias</strong>
              <span>Escolha um período disponível.</span>
            </Link>
            <Link className="quick-action" to="/disponibilidade">
              <strong>Ver calendário</strong>
              <span>Confira datas bloqueadas.</span>
            </Link>
            <Link className="quick-action" to="/minhas-ferias">
              <strong>Minhas férias</strong>
              <span>Histórico de solicitações.</span>
            </Link>
            <Link className="quick-action" to="/mural">
              <strong>Mural de avisos</strong>
              <span>Comunicados e informações.</span>
            </Link>
          </div>
        </section>
      </div>

      {avisos.length > 0 && (
        <section className="card">
          <div className="card-header">
            <h2 className="card-title">Mural de avisos</h2>
            <Link className="btn btn-outline btn-sm" to="/mural">Ver todos</Link>
          </div>
          <div className="card-body avisos-lista">
            {avisos.slice(0, 3).map(aviso => (
              <AvisoCard key={aviso.id} aviso={aviso} />
            ))}
          </div>
        </section>
      )}
    </>
  )
}
