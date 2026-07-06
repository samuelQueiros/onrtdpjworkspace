import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'

export default function RelatorioTabela({ colaboradores, filtro, onFiltroChange }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Resumo por colaborador</h2>
        <input
          className="search-input"
          placeholder="Filtrar por nome ou departamento..."
          value={filtro}
          onChange={event => onFiltroChange(event.target.value)}
        />
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Departamento</th>
              <th>Total</th>
              <th>Usados</th>
              <th>Restantes</th>
              <th>Pendentes</th>
              <th>Períodos</th>
            </tr>
          </thead>
          <tbody>
            {colaboradores.map(item => (
              <tr key={item.id}>
                <td>{item.nome}</td>
                <td>{item.email}</td>
                <td>{item.departamento?.nome || <span className="muted">-</span>}</td>
                <td>{item.dias_totais}</td>
                <td>{item.dias_usados}</td>
                <td>
                  <StatusBadge tone={item.dias_restantes > 10 ? 'green' : item.dias_restantes > 0 ? 'amber' : 'red'}>
                    {item.dias_restantes}
                  </StatusBadge>
                </td>
                <td>
                  {item.ferias_pendentes.length > 0
                    ? <StatusBadge tone="amber">{item.ferias_pendentes.length}</StatusBadge>
                    : <span className="muted">-</span>}
                </td>
                <td>
                  {item.ferias.length
                    ? item.ferias.map(ferias => `${formatDate(ferias.data_inicio)}-${formatDate(ferias.data_fim)}`).join(', ')
                    : <span className="muted">-</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
