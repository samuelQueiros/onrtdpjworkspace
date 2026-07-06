export default function PermissoesUsuarios({ userIds, usuarios, onToggleUsuario }) {
  if (!usuarios.length) return null

  return (
    <div className="form-group">
      <label>Permissões</label>
      <div className="stack-6 mt-4">
        {usuarios.map(usuario => (
          <label key={usuario.id} className="permission-option">
            <input
              type="checkbox"
              checked={userIds.includes(usuario.id)}
              onChange={() => onToggleUsuario(usuario.id)}
            />
            {usuario.nome}
          </label>
        ))}
      </div>
    </div>
  )
}
