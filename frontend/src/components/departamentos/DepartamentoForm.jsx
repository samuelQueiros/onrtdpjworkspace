export const blankDepartamentoForm = { nome: '', limite_simultaneo: 2 }

export default function DepartamentoForm({ editing, form, onCancel, onChange, onSubmit }) {
  const updateForm = changes => onChange({ ...form, ...changes })

  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <h2 className="card-title">{editing ? 'Editar departamento' : 'Novo departamento'}</h2>
      </div>
      <div className="card-body form-stack">
        <div className="form-group">
          <label>Nome do setor</label>
          <input
            value={form.nome}
            onChange={event => updateForm({ nome: event.target.value })}
            placeholder="Ex: Tecnologia da Informação"
            required
          />
        </div>
        <div className="form-group">
          <label>Limite de férias simultâneas</label>
          <input
            type="number"
            min="1"
            max="50"
            value={form.limite_simultaneo}
            onChange={event => updateForm({ limite_simultaneo: event.target.value })}
            required
          />
          <small className="form-hint">
            Máximo de colaboradores do setor em férias ao mesmo tempo.
          </small>
        </div>

        <div className="button-row">
          {editing && (
            <button className="btn btn-outline" type="button" onClick={onCancel}>
              Cancelar
            </button>
          )}
          <button className="btn btn-primary" type="submit">
            {editing ? 'Salvar alterações' : 'Criar departamento'}
          </button>
        </div>
      </div>
    </form>
  )
}
