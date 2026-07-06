export const blankAvisoForm = { titulo: '', conteudo: '', fixado: false, data_expiracao: '' }

export default function AvisoForm({ editing, form, onCancel, onChange, onSubmit }) {
  const updateForm = changes => onChange({ ...form, ...changes })

  return (
    <section className="card spaced">
      <div className="card-header">
        <h2 className="card-title">{editing ? 'Editar aviso' : 'Publicar novo aviso'}</h2>
      </div>
      <form onSubmit={onSubmit}>
        <div className="card-body form-stack">
          <div className="form-group">
            <label>Título</label>
            <input
              type="text"
              value={form.titulo}
              onChange={event => updateForm({ titulo: event.target.value })}
              placeholder="Título do aviso"
              required
            />
          </div>
          <div className="form-group">
            <label>Conteúdo</label>
            <textarea
              value={form.conteudo}
              onChange={event => updateForm({ conteudo: event.target.value })}
              rows={4}
              placeholder="Texto do comunicado..."
              required
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Data de expiração (opcional)</label>
              <input
                type="date"
                value={form.data_expiracao}
                onChange={event => updateForm({ data_expiracao: event.target.value })}
              />
            </div>
            <div className="form-group">
              <label>&nbsp;</label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={form.fixado}
                  onChange={event => updateForm({ fixado: event.target.checked })}
                />
                <span>Fixar aviso no topo</span>
              </label>
            </div>
          </div>
          <div className="button-row">
            <button className="btn btn-outline" type="button" onClick={onCancel}>
              Cancelar
            </button>
            <button className="btn btn-primary" type="submit">
              {editing ? 'Salvar alterações' : 'Publicar aviso'}
            </button>
          </div>
        </div>
      </form>
    </section>
  )
}
