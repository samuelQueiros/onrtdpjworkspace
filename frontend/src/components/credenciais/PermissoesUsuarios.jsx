export default function PermissoesUsuarios({ userIds, usuarios, onToggleUsuario }) {
  if (!usuarios.length) return null

  return (
    <div className="form-group">
      <label>Permissões</label>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 4 }}>
        {usuarios.map(usuario => (
          <label key={usuario.id} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontWeight: 'normal' }}>
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
