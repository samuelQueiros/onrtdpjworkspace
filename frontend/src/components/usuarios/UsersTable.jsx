import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import UserColorDot from './UserColorDot'

export default function UsersTable({
  users,
  currentUserId,
  detailsLoadingId,
  onDetails,
  onEdit,
  onDelete,
  onReactivate,
}) {
  return (
    <section className="card users-table-card">
      <div className="card-header"><h2 className="card-title">Colaboradores ({users.length})</h2></div>
      <div className="table-wrap">
        <table className="users-table">
          <thead>
            <tr>
              <th>Colaborador</th>
              <th>Cargo / Departamento</th>
              <th>Telefone</th>
              <th>Perfil</th>
              <th>Status</th>
              <th>Aniversário</th>
              <th>Saldo de férias</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>
                  <div className="user-identity-cell">
                    <UserColorDot color={user.cor} />
                    <div className="user-identity-text">
                      <strong>{user.nome}</strong>
                      <span className="cell-sub">{user.email}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div className="user-identity-text">
                    <span>{user.cargo || <span className="muted">Sem cargo</span>}</span>
                    <span className="cell-sub">{user.departamento?.nome || 'Sem departamento'}</span>
                  </div>
                </td>
                <td>{user.telefone || <span className="muted">-</span>}</td>
                <td>
                  <StatusBadge tone={user.role === 'admin' ? 'navy' : 'gray'}>
                    {user.role === 'admin' ? 'Admin' : 'Usuário'}
                  </StatusBadge>
                </td>
                <td><StatusBadge tone={user.ativo ? 'green' : 'red'}>{user.ativo ? 'Ativo' : 'Inativo'}</StatusBadge></td>
                <td>{user.data_aniversario ? formatDate(user.data_aniversario) : <span className="muted">-</span>}</td>
                <td>
                  <div className="user-identity-text">
                    <strong>{user.dias_restantes} dia(s)</strong>
                    <span className="cell-sub">{user.dias_usados_total ?? 0} usado(s) no total</span>
                  </div>
                </td>
                <td className="actions-cell">
                  <button
                    className="btn btn-primary btn-sm"
                    type="button"
                    onClick={() => onDetails(user)}
                    disabled={detailsLoadingId !== null}
                  >
                    {detailsLoadingId === user.id ? 'Abrindo...' : 'Detalhes'}
                  </button>
                  <button
                    className="btn btn-outline btn-sm"
                    type="button"
                    onClick={() => onEdit(user)}
                    disabled={detailsLoadingId !== null}
                  >
                    Editar
                  </button>
                  {user.id !== currentUserId && user.ativo && (
                    <button
                      className="btn btn-danger btn-sm"
                      type="button"
                      onClick={() => onDelete(user.id)}
                      disabled={detailsLoadingId !== null}
                    >
                      Desativar
                    </button>
                  )}
                  {!user.ativo && (
                    <button
                      className="btn btn-primary btn-sm"
                      type="button"
                      onClick={() => onReactivate(user.id)}
                      disabled={detailsLoadingId !== null}
                    >
                      Reativar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
