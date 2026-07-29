export default function UploadDocumentoForm({
  fileRef,
  isAdmin,
  destinoTipo,
  onDestinoTipoChange,
  observacao,
  onObservacaoChange,
  onSubmit,
  onTargetUserChange,
  onTipoChange,
  targetUser,
  tipo,
  uploading,
  users,
}) {
  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header"><h2 className="card-title">Enviar documento</h2></div>
      <div className="card-body form-stack">
        <div className="form-group">
          <label htmlFor="documento-tipo">Tipo de documento</label>
          <select id="documento-tipo" name="tipo" value={tipo} onChange={event => onTipoChange(event.target.value)}>
            <option value="atestado">Atestado médico</option>
            {isAdmin && <option value="contracheque">Contracheque</option>}
            <option value="outro">Documento geral</option>
          </select>
        </div>

        {isAdmin && (
          <>
            <div className="form-group">
              <label htmlFor="documento-destino">Destino</label>
              <select
                id="documento-destino"
                name="destino_tipo"
                value={destinoTipo}
                onChange={event => onDestinoTipoChange(event.target.value)}
              >
                <option value="usuario">Caixa pessoal de um usuário</option>
                <option value="administracao">Administração — caixa geral</option>
              </select>
            </div>
            {destinoTipo === 'usuario' && <div className="form-group">
              <label htmlFor="documento-usuario">Destinatário</label>
              <select
                id="documento-usuario" name="user_id"
                value={targetUser}
                onChange={event => onTargetUserChange(event.target.value)}
                required
              >
                <option value="">Selecione...</option>
                {users.map(user => (
                  <option key={user.id} value={user.id}>{user.nome}</option>
                ))}
              </select>
            </div>}
          </>
        )}

        <div className="form-group">
          <label htmlFor="documento-arquivo">Arquivo (PDF, JPG, PNG - máx. 10 MB)</label>
          <input id="documento-arquivo" name="file" ref={fileRef} type="file" accept=".pdf,.jpg,.jpeg,.png" required />
        </div>

        <div className="form-group">
          <div className="document-observation-label">
            <label htmlFor="documento-observacao">Observações (opcional)</label>
            <span>{observacao.length}/2000</span>
          </div>
          <textarea
            id="documento-observacao"
            name="observacao"
            value={observacao}
            onChange={event => onObservacaoChange(event.target.value)}
            rows="4"
            maxLength="2000"
            placeholder="Inclua informações úteis para quem receberá o documento."
          />
        </div>

        <button className="btn btn-primary" type="submit" disabled={uploading}>
          {uploading ? 'Enviando...' : 'Enviar documento'}
        </button>
      </div>
    </form>
  )
}
