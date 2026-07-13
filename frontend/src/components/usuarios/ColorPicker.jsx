const CORES_SUGERIDAS = [
  '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#f97316', '#ec4899', '#10b981', '#6366f1',
]

export default function ColorPicker({ value, onChange }) {
  return (
    <div className="color-picker">
      <div className="color-swatches">
        {CORES_SUGERIDAS.map(cor => (
          <button
            key={cor}
            type="button"
            className={`color-swatch${value === cor ? ' selected' : ''}`}
            style={{ background: cor }}
            onClick={() => onChange(value === cor ? '' : cor)}
            title={cor}
          />
        ))}
      </div>
      <div className="color-custom">
        <input
          type="color"
          value={value || '#3b82f6'}
          onChange={event => onChange(event.target.value)}
          title="Cor personalizada"
        />
        <input
          id="user-cor"
          type="text"
          className="color-hex-input"
          value={value}
          onChange={event => onChange(event.target.value)}
          placeholder="#000000"
          maxLength={7}
          required
        />
        {value && (
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => onChange('')}
          >
            Limpar
          </button>
        )}
      </div>
    </div>
  )
}
