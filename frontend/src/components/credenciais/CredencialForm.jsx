import PermissoesUsuarios from './PermissoesUsuarios'

export const blankCredencialForm = { descricao: '', email: '', senha: '' }

export default function CredencialForm({
  editing,
  form,
  mostrarSenha,
  onCancel,
  onChange,
  onSubmit,
  onToggleSenha,
  onToggleUsuario,
  userIds,
  usuarios,
}) {
  const updateForm = changes => onChange({ ...form, ...changes })

  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <h2 className="card-title">{editing === 'nova' ? 'Nova credencial' : 'Editar credencial'}</h2>
      </div>
      <div className="card-body form-stack">
        <div className="form-group">
          <label htmlFor="credencial-descricao">Descrição</label>
          <input
            id="credencial-descricao" name="descricao"
            type="text"
            value={form.descricao}
            onChange={event => updateForm({ descricao: event.target.value })}
            placeholder="Ex.: Google Workspace, Meta Business..."
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="credencial-email">E-mail</label>
          <input
            id="credencial-email" name="email" autoComplete="username"
            type="text"
            value={form.email}
            onChange={event => updateForm({ email: event.target.value })}
            placeholder="usuario@empresa.com"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="credencial-senha">Senha</label>
          <div className="field-with-action">
            <input
              id="credencial-senha" name="senha" autoComplete="new-password"
              type={mostrarSenha ? 'text' : 'password'}
              value={form.senha}
              onChange={event => updateForm({ senha: event.target.value })}
              placeholder={editing === 'nova' ? 'Senha de acesso' : 'Deixe em branco para manter a senha atual'}
              required={editing === 'nova'}
              className="flex-1"
            />
            <button
              type="button"
              onClick={onToggleSenha}
              className="btn btn-outline btn-sm nowrap"
            >
              {mostrarSenha ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>
        </div>

        <PermissoesUsuarios
          userIds={userIds}
          usuarios={usuarios}
          onToggleUsuario={onToggleUsuario}
        />

        <div className="button-row">
          <button className="btn btn-outline" type="button" onClick={onCancel}>
            Cancelar
          </button>
          <button className="btn btn-primary" type="submit">
            {editing === 'nova' ? 'Criar credencial' : 'Salvar alterações'}
          </button>
        </div>
      </div>
    </form>
  )
}
