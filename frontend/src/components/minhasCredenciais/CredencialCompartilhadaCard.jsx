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
      <div className="card-body stack-12">
        <div className="inline-center gap-8">
          <span className="credential-field-label">E-mail</span>
          <span className="flex-1">{credencial.email}</span>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onCopiar(`email-${credencial.id}`, credencial.email)}
          >
            {copiado[`email-${credencial.id}`] ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <div className="inline-center gap-8">
          <span className="credential-field-label">Senha</span>
          <span className={`credential-secret${visivel ? '' : ' masked'}`}>
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
