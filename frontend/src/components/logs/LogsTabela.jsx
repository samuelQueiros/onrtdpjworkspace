import { EmptyState } from '../../pages/_helpers'
import { formatDateTime } from '../../utils/formatters'

export default function LogsTabela({ logs, search, onSearchChange }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Registros ({logs.length})</h2>
        <input
          className="search-input"
          placeholder="Filtrar por usuário, ação ou detalhe..."
          value={search}
          onChange={event => onSearchChange(event.target.value)}
        />
      </div>
      <div className="table-wrap">
        {logs.length ? (
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Ação</th>
                <th>Usuário</th>
                <th>E-mail</th>
                <th>Detalhes</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td className="nowrap">{formatDateTime(log.criado_em)}</td>
                  <td><code className="action-code">{log.acao}</code></td>
                  <td>{log.nome_usuario || `#${log.user_id}`}</td>
                  <td className="muted">{log.email_usuario || '-'}</td>
                  <td>{log.detalhes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState title="Sem logs" text="As ações administrativas aparecerão aqui." />
        )}
      </div>
    </section>
  )
}
