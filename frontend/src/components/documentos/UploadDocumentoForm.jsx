export default function UploadDocumentoForm({
  fileRef,
  isAdmin,
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
          <label>Tipo de documento</label>
          <select value={tipo} onChange={event => onTipoChange(event.target.value)}>
            <option value="atestado">Atestado médico</option>
            {isAdmin && <option value="contracheque">Contracheque</option>}
          </select>
        </div>

        {isAdmin && (
          <div className="form-group">
            <label>Colaborador</label>
            <select
              value={targetUser}
              onChange={event => onTargetUserChange(event.target.value)}
              required
            >
              <option value="">Selecione...</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>{user.nome}</option>
              ))}
            </select>
          </div>
        )}

        <div className="form-group">
          <label>Arquivo (PDF, JPG, PNG - máx. 10 MB)</label>
          <input ref={fileRef} type="file" accept=".pdf,.jpg,.jpeg,.png" required />
        </div>

        <button className="btn btn-primary" type="submit" disabled={uploading}>
          {uploading ? 'Enviando...' : 'Enviar documento'}
        </button>
      </div>
    </form>
  )
}
