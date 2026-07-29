const STATUS_OPTIONS = [
  ['pendente', 'Pendentes'],
  ['aguardando_entrega', 'Aguardando entrega'],
  ['aguardando_aceite', 'Aguardando aceite'],
  ['aceite_registrado_aguardando_documento', 'Gerando termo'],
  ['entregue', 'Entregues'],
  ['devolvida', 'Devolvidas'],
  ['rejeitada', 'Rejeitadas'],
  ['cancelada', 'Canceladas'],
]

export default function FiltrosAutorizacoesEquipamentos({ filters, loading, onChange, onClear, onSubmit, users }) {
  const update = event => onChange({ ...filters, [event.target.name]: event.target.value })

  return (
    <form className="card autorizacao-filtros" onSubmit={onSubmit} aria-label="Filtros das autorizações de equipamentos">
      <div className="autorizacao-filtros-grid">
        <div className="form-group">
          <label htmlFor="autorizacao-status">Status</label>
          <select id="autorizacao-status" name="status" value={filters.status} onChange={update}>
            <option value="">Todos os status</option>
            {STATUS_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="autorizacao-colaborador">Colaborador</label>
          <select id="autorizacao-colaborador" name="user_id" value={filters.user_id} onChange={update}>
            <option value="">Todos os colaboradores</option>
            {users.map(user => <option key={user.id} value={user.id}>{user.nome}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="autorizacao-equipamento">Equipamento (ID)</label>
          <input
            id="autorizacao-equipamento"
            name="equipamento_id"
            type="number"
            min="1"
            inputMode="numeric"
            value={filters.equipamento_id}
            onChange={update}
            placeholder="Ex.: 12"
          />
        </div>

        <div className="form-group">
          <label htmlFor="autorizacao-data-inicial">Solicitado a partir de</label>
          <input id="autorizacao-data-inicial" name="criado_de" type="date" value={filters.criado_de} onChange={update} />
        </div>

        <div className="form-group">
          <label htmlFor="autorizacao-data-final">Solicitado até</label>
          <input id="autorizacao-data-final" name="criado_ate" type="date" value={filters.criado_ate} onChange={update} />
        </div>
      </div>

      <div className="autorizacao-filtros-actions">
        <button className="btn btn-outline" type="button" onClick={onClear} disabled={loading}>Limpar</button>
        <button className="btn btn-navy" type="submit" disabled={loading}>
          {loading ? 'Filtrando...' : 'Aplicar filtros'}
        </button>
      </div>
    </form>
  )
}
