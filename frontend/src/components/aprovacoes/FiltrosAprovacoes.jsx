const TABS = [
  { key: 'pendente', label: 'Pendentes' },
  { key: 'aprovada', label: 'Aprovadas' },
  { key: 'rejeitada', label: 'Rejeitadas' },
  { key: 'todas', label: 'Todas' },
]

export default function FiltrosAprovacoes({ counts, filtro, onChange }) {
  return (
    <div className="filter-tabs spaced">
      {TABS.map(tab => (
        <button
          key={tab.key}
          className={`filter-tab${filtro === tab.key ? ' active' : ''}`}
          onClick={() => onChange(tab.key)}
        >
          {tab.label}
          <span className="filter-tab-count">{counts[tab.key]}</span>
        </button>
      ))}
    </div>
  )
}
