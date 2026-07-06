const TABS = [
  { key: 'todos', label: 'Todos' },
  { key: 'bloqueio', label: 'Bloqueios' },
  { key: 'recesso', label: 'Recessos' },
]

export default function FiltrosBloqueios({ bloqueios, filtro, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 8 }}>
      {TABS.map(tab => (
        <button
          key={tab.key}
          className={`filter-tab sm${filtro === tab.key ? ' active' : ''}`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
          <span className="filter-tab-count">
            {tab.key === 'todos' ? bloqueios.length : bloqueios.filter(bloqueio => bloqueio.tipo === tab.key).length}
          </span>
        </button>
      ))}
    </div>
  )
}
