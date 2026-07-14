import { TIPO_EQUIPAMENTO } from './statusAutorizacoes'

export default function EquipamentoSelecionavel({ equipamento, checked, onChange }) {
  return (
    <label className={`equipment-choice${checked ? ' selected' : ''}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={() => onChange(equipamento.id)}
      />
      <span>
        <strong>{TIPO_EQUIPAMENTO[equipamento.tipo] || equipamento.tipo} — {equipamento.marca} {equipamento.modelo}</strong>
        <small>
          Patrimônio: {equipamento.numero_patrimonio || 'não informado'} · Série: {equipamento.numero_serie || 'não informada'}
        </small>
        <small>Conservação: {equipamento.estado_conservacao}</small>
      </span>
    </label>
  )
}
