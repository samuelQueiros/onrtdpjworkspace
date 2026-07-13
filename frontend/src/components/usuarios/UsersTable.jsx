import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import UserColorDot from './UserColorDot'

export default function UsersTable({ users, currentUserId, onEdit, onDelete, onReactivate }) {
  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Colaboradores ({users.length})</h2></div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Cor</th>
              <th>Nome</th>
              <th>E-mail</th>
              <th>Cargo</th>
              <th>Telefone</th>
              <th>Perfil</th>
              <th>Status</th>
              <th>Departamento</th>
              <th>Aniversário</th>
              <th>Saldo</th>
              <th>Total</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td><UserColorDot color={user.cor} /></td>
                <td><strong>{user.nome}</strong></td>
                <td>{user.email}</td>
                <td>{user.cargo || <span className="muted">-</span>}</td>
                <td>{user.telefone || <span className="muted">-</span>}</td>
                <td>
                  <StatusBadge tone={user.role === 'admin' ? 'navy' : 'gray'}>
                    {user.role === 'admin' ? 'Admin' : 'Usuário'}
                  </StatusBadge>
                </td>
                <td><StatusBadge tone={user.ativo ? 'green' : 'red'}>{user.ativo ? 'Ativo' : 'Inativo'}</StatusBadge></td>
                <td>{user.departamento?.nome || <span className="muted">-</span>}</td>
                <td>{user.data_aniversario ? formatDate(user.data_aniversario) : <span className="muted">-</span>}</td>
                <td>{user.dias_restantes}</td>
                <td>{user.dias_totais}</td>
                <td className="actions-cell">
                  <button className="btn btn-outline btn-sm" onClick={() => onEdit(user)}>
                    Editar
                  </button>
                  {user.id !== currentUserId && user.ativo && (
                    <button className="btn btn-danger btn-sm" onClick={() => onDelete(user.id)}>
                      Desativar
                    </button>
                  )}
                  {!user.ativo && (
                    <button className="btn btn-primary btn-sm" onClick={() => onReactivate(user.id)}>Reativar</button>
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
