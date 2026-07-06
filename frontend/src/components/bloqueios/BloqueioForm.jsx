export const blankBloqueioForm = { data_inicio: '', data_fim: '', motivo: '', tipo: 'bloqueio' }

export default function BloqueioForm({ editing, error, form, onCancel, onChange, onSubmit, success }) {
  const updateForm = changes => onChange({ ...form, ...changes })

  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <h2 className="card-title">{editing ? 'Editar período' : 'Novo período'}</h2>
      </div>
      <div className="card-body form-stack">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="form-group">
          <label>Tipo</label>
          <select value={form.tipo} onChange={event => updateForm({ tipo: event.target.value })}>
            <option value="bloqueio">Bloqueio - impede novas solicitações</option>
            <option value="recesso">Recesso - período coletivo de folga</option>
          </select>
        </div>

        <div className="form-group">
          <label>Motivo / Descrição</label>
          <input
            type="text"
            value={form.motivo}
            onChange={event => updateForm({ motivo: event.target.value })}
            placeholder="Ex.: Auditoria interna, Recesso de Natal..."
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Data início</label>
            <input
              type="date"
              value={form.data_inicio}
              onChange={event => updateForm({ data_inicio: event.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Data fim</label>
            <input
              type="date"
              value={form.data_fim}
              onChange={event => updateForm({ data_fim: event.target.value })}
              required
            />
          </div>
        </div>

        {form.tipo === 'bloqueio' && (
          <div className="alert alert-info">
            <p>Colaboradores <strong>não poderão</strong> solicitar férias neste período. Uma mensagem amigável será exibida ao tentar.</p>
          </div>
        )}
        {form.tipo === 'recesso' && (
          <div className="alert alert-info">
            O recesso aparece destacado no calendário. Colaboradores verão o período como recesso coletivo.
          </div>
        )}

        <div className="button-row">
          {editing && (
            <button className="btn btn-outline" type="button" onClick={onCancel}>
              Cancelar
            </button>
          )}
          <button className="btn btn-primary" type="submit">
            {editing ? 'Salvar alterações' : 'Cadastrar período'}
          </button>
        </div>
      </div>
    </form>
  )
}
