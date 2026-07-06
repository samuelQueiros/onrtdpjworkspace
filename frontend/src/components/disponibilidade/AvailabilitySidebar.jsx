import { StatusBadge } from '../../pages/_helpers'
import { formatDate } from '../../utils/formatters'

export default function AvailabilitySidebar({ bloqueiosManuais, feriasMarcadas, periodos }) {
  return (
    <aside>
      <section className="card" style={{ marginBottom: 16 }}>
        <div className="card-header">
          <h2 className="card-title">Férias marcadas</h2>
          <StatusBadge tone={feriasMarcadas.length > 0 ? 'green' : 'gray'}>
            {feriasMarcadas.length}
          </StatusBadge>
        </div>
        <div className="card-body blocked-list">
          {feriasMarcadas.length ? feriasMarcadas.map(item => (
            <div className="vacation-item" key={item.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <span style={{ width: 12, height: 12, borderRadius: '50%', background: item.cor || '#64748b', flexShrink: 0, marginTop: 3 }} />
              <div>
                <strong>
                  {item.nome}
                  {item.ferias_acordo && <StatusBadge tone="blue">Por acordo</StatusBadge>}
                </strong>
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                  {formatDate(item.data_inicio)} a {formatDate(item.data_fim)} - {item.dias_usados} dia(s)
                </div>
              </div>
            </div>
          )) : <p className="muted">Sem férias aprovadas.</p>}
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Bloqueios e Recessos</h2>
          <StatusBadge tone={bloqueiosManuais.length > 0 ? 'red' : 'gray'}>
            {bloqueiosManuais.length}
          </StatusBadge>
        </div>
        <div className="card-body blocked-list">
          {bloqueiosManuais.length ? bloqueiosManuais.map(bloqueio => (
            <div className="blocked-item" key={bloqueio.id}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <StatusBadge tone={bloqueio.tipo === 'recesso' ? 'blue' : 'red'}>
                  {bloqueio.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                </StatusBadge>
                <strong>{bloqueio.motivo}</strong>
              </div>
              <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                {formatDate(bloqueio.data_inicio)} a {formatDate(bloqueio.data_fim)}
              </span>
            </div>
          )) : <p className="muted">Sem bloqueios cadastrados.</p>}

          <div className="divider" />
          <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Bloqueios por limite de equipe</h3>
          {periodos.length ? periodos.map((periodo, index) => (
            <div className="blocked-item" key={index}>
              <strong>{formatDate(periodo.data_inicio)} a {formatDate(periodo.data_fim)}</strong>
              <span style={{ fontSize: 12, color: 'var(--muted)' }}>Limite simultâneo atingido</span>
            </div>
          )) : <p className="muted">Sem datas bloqueadas por limite.</p>}
        </div>
      </section>
    </aside>
  )
}
