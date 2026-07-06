import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatBytes, formatDate } from '../../utils/formatters'
import { TIPO_LABEL, TIPO_TONE } from './documentosLabels'

export default function DocumentosTabela({
  docs,
  isAdmin,
  loading,
  onDelete,
  onDownload,
  onUserFilter,
  selectedUser,
  users,
}) {
  return (
    <section className="card">
      {isAdmin ? (
        <div className="card-header">
          <h2 className="card-title">Documentos</h2>
          <select
            value={selectedUser}
            onChange={event => onUserFilter(event.target.value)}
            className="select-filter"
          >
            <option value="">Selecione um colaborador...</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>{user.nome}</option>
            ))}
          </select>
        </div>
      ) : (
        <div className="card-header"><h2 className="card-title">Meus documentos</h2></div>
      )}

      <div className="table-wrap">
        {loading ? (
          <div className="empty"><div className="spinner" /><p>Carregando...</p></div>
        ) : docs.length ? (
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Arquivo</th>
                <th>Tamanho</th>
                <th>Enviado por</th>
                <th>Data</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id}>
                  <td>
                    <StatusBadge tone={TIPO_TONE[doc.tipo] || 'gray'}>
                      {TIPO_LABEL[doc.tipo] || doc.tipo}
                    </StatusBadge>
                  </td>
                  <td>{doc.nome_arquivo}</td>
                  <td>{formatBytes(doc.tamanho)}</td>
                  <td>{doc.criado_por_nome}</td>
                  <td>{formatDate(doc.criado_em)}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" onClick={() => onDownload(doc.id)}>
                      Download
                    </button>
                    {isAdmin && (
                      <button className="btn btn-danger btn-sm" onClick={() => onDelete(doc.id)}>
                        Excluir
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title="Nenhum documento"
            text={isAdmin && !selectedUser ? 'Selecione um colaborador para ver seus documentos.' : 'Nenhum documento encontrado.'}
          />
        )}
      </div>
    </section>
  )
}
