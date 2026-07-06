export default function CredencialCompartilhadaCard({
  copiado,
  credencial,
  onCopiar,
  onToggleVisivel,
  visivel,
}) {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{credencial.descricao}</h2>
      </div>
      <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ minWidth: 60, color: 'var(--muted)', fontSize: 13 }}>E-mail</span>
          <span style={{ flex: 1 }}>{credencial.email}</span>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onCopiar(`email-${credencial.id}`, credencial.email)}
          >
            {copiado[`email-${credencial.id}`] ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ minWidth: 60, color: 'var(--muted)', fontSize: 13 }}>Senha</span>
          <span style={{ flex: 1, fontFamily: 'monospace', letterSpacing: visivel ? 0 : 2 }}>
            {visivel ? credencial.senha : '********'}
          </span>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onToggleVisivel(credencial.id)}
          >
            {visivel ? 'Ocultar' : 'Mostrar'}
          </button>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onCopiar(`senha-${credencial.id}`, credencial.senha)}
          >
            {copiado[`senha-${credencial.id}`] ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
      </div>
    </div>
  )
}
