import ColorPicker from './ColorPicker'
import UserColorDot from './UserColorDot'

export const blankUserForm = {
  nome: '',
  email: '',
  senha: '',
  role: 'user',
  dias_totais: 30,
  departamento_id: '',
  data_admissao: '',
  data_aniversario: '',
  cor: '',
}

export default function UserForm({
  departamentos,
  editing,
  error,
  form,
  onCancel,
  onChange,
  onSubmit,
  success,
}) {
  const updateForm = changes => onChange({ ...form, ...changes })

  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <h2 className="card-title">{editing ? 'Editar usuário' : 'Novo usuário'}</h2>
      </div>
      <div className="card-body form-stack">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div className="form-group">
          <label>Nome</label>
          <input
            type="text"
            value={form.nome}
            onChange={event => updateForm({ nome: event.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>E-mail</label>
          <input
            type="email"
            value={form.email}
            onChange={event => updateForm({ email: event.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label>{editing ? 'Nova senha (deixe em branco para manter)' : 'Senha'}</label>
          <input
            type="password"
            value={form.senha}
            onChange={event => updateForm({ senha: event.target.value })}
            required={!editing}
          />
        </div>
        {!editing && (
          <div className="form-group">
            <label>Perfil</label>
            <select value={form.role} onChange={event => updateForm({ role: event.target.value })}>
              <option value="user">Usuário</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
        )}
        <div className="form-group">
          <label>Departamento</label>
          <select
            value={form.departamento_id}
            onChange={event => updateForm({ departamento_id: event.target.value })}
          >
            <option value="">Sem departamento</option>
            {departamentos.map(departamento => (
              <option key={departamento.id} value={departamento.id}>{departamento.nome}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>
            Cor de identificação
            {form.cor && (
              <span style={{ marginLeft: 8 }}>
                <UserColorDot color={form.cor} size={14} />
              </span>
            )}
          </label>
          <ColorPicker value={form.cor} onChange={cor => updateForm({ cor })} />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Dias totais</label>
            <input
              type="number"
              min="0"
              value={form.dias_totais}
              onChange={event => updateForm({ dias_totais: event.target.value })}
              required
            />
          </div>
          <div className="form-group">
            <label>Data de admissão</label>
            <input
              type="date"
              value={form.data_admissao}
              onChange={event => updateForm({ data_admissao: event.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Data de aniversário</label>
            <input
              type="date"
              value={form.data_aniversario}
              onChange={event => updateForm({ data_aniversario: event.target.value })}
            />
          </div>
        </div>

        <div className="button-row">
          {editing && (
            <button className="btn btn-outline" type="button" onClick={onCancel}>
              Cancelar
            </button>
          )}
          <button className="btn btn-primary" type="submit">
            {editing ? 'Salvar alterações' : 'Criar usuário'}
          </button>
        </div>
      </div>
    </form>
  )
}
