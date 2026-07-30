export default function ColaboradorSelect({ colaboradores, selectedId, onChange }) {
  return (
    <div className="form-group estatisticas-select-group">
      <label htmlFor="estatisticas-colaborador">Colaborador</label>
      <select
        id="estatisticas-colaborador"
        value={selectedId ?? ''}
        onChange={event => onChange(event.target.value ? Number(event.target.value) : null)}
      >
        <option value="">Selecione um colaborador</option>
        {colaboradores.map(colaborador => (
          <option key={colaborador.id} value={colaborador.id}>
            {colaborador.nome}{colaborador.departamento?.nome ? ` · ${colaborador.departamento.nome}` : ''}
          </option>
        ))}
      </select>
    </div>
  )
}
