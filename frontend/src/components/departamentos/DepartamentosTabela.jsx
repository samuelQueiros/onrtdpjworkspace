import { StatusBadge } from '../../pages/_helpers'

export default function DepartamentosTabela({ departamentos, onDelete, onEdit }) {
  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Setores cadastrados</h2></div>
      <div className="table-wrap">
        {departamentos.length ? (
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Limite simultâneo</th>
                <th>Usuários</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {departamentos.map(dep => (
                <tr key={dep.id}>
                  <td><strong>{dep.nome}</strong></td>
                  <td>
                    <StatusBadge tone="navy">{dep.limite_simultaneo} simultâneo(s)</StatusBadge>
                  </td>
                  <td>{dep.total_usuarios}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" onClick={() => onEdit(dep)}>Editar</button>
                    <button className="btn btn-danger btn-sm" onClick={() => onDelete(dep.id)}>Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty">
            <p>Nenhum departamento cadastrado.</p>
          </div>
        )}
      </div>
    </section>
  )
}
