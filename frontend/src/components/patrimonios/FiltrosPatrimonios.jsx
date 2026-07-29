/* eslint-disable react-refresh/only-export-components */
import { STATUS_EQUIPAMENTO, TIPOS_EQUIPAMENTO } from './patrimoniosLabels'

export const blankPatrimonioFilters = {
  busca: '',
  tipo: '',
  status: '',
  ativo: '',
  user_id: '',
}

export default function FiltrosPatrimonios({ filters, users, onChange, onClear, onSubmit, busy }) {
  const update = changes => onChange({ ...filters, ...changes })

  return (
    <form className="card patrimonio-filters" onSubmit={onSubmit} aria-label="Filtros de patrimônios">
      <div className="patrimonio-filters-grid">
        <div className="form-group patrimonio-search-field">
          <label htmlFor="patrimonio-busca">Buscar</label>
          <input
            id="patrimonio-busca"
            name="busca"
            type="search"
            value={filters.busca}
            onChange={event => update({ busca: event.target.value })}
            placeholder="Patrimônio, série, tipo, marca, modelo ou colaborador"
          />
        </div>

        <div className="form-group">
          <label htmlFor="patrimonio-tipo">Tipo</label>
          <select id="patrimonio-tipo" name="tipo" value={filters.tipo} onChange={event => update({ tipo: event.target.value })}>
            <option value="">Todos</option>
            {TIPOS_EQUIPAMENTO.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="patrimonio-status">Status</label>
          <select id="patrimonio-status" name="status" value={filters.status} onChange={event => update({ status: event.target.value })}>
            <option value="">Todos</option>
            {STATUS_EQUIPAMENTO.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="patrimonio-ativo">Situação</label>
          <select id="patrimonio-ativo" name="ativo" value={filters.ativo} onChange={event => update({ ativo: event.target.value })}>
            <option value="">Ativos e inativos</option>
            <option value="true">Ativos</option>
            <option value="false">Inativos</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="patrimonio-colaborador">Colaborador</label>
          <select id="patrimonio-colaborador" name="user_id" value={filters.user_id} onChange={event => update({ user_id: event.target.value })}>
            <option value="">Todos</option>
            {users.map(user => <option key={user.id} value={user.id}>{user.nome}</option>)}
          </select>
        </div>
      </div>

      <div className="patrimonio-filter-actions">
        <button className="btn btn-outline" type="button" onClick={onClear} disabled={busy}>Limpar filtros</button>
        <button className="btn btn-navy" type="submit" disabled={busy}>
          {busy ? 'Filtrando...' : 'Aplicar filtros'}
        </button>
      </div>
    </form>
  )
}
