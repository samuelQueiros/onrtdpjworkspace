import { EmptyState } from '../comum/PageHelpers'

export default function CredenciaisTabela({ credenciais, editing, onDelete, onEdit, onNew }) {
  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Credenciais cadastradas</h2>
        {!editing && (
          <button className="btn btn-primary btn-sm" onClick={onNew}>
            + Nova Credencial
          </button>
        )}
      </div>
      <div className="table-wrap">
        {credenciais.length ? (
          <table>
            <thead>
              <tr>
                <th>Descrição</th>
                <th>E-mail</th>
                <th>Usuários com acesso</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {credenciais.map(credencial => (
                <tr key={credencial.id}>
                  <td><strong>{credencial.descricao}</strong></td>
                  <td>{credencial.email}</td>
                  <td>{credencial.total_usuarios} {credencial.total_usuarios === 1 ? 'usuário' : 'usuários'}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" onClick={() => onEdit(credencial)}>
                      Editar
                    </button>
                    <button className="btn btn-danger btn-sm" onClick={() => onDelete(credencial.id)}>
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title="Nenhuma credencial cadastrada"
            text="Cadastre credenciais para compartilhar acessos com a equipe."
          />
        )}
      </div>
    </section>
  )
}
