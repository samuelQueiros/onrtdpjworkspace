import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'

export default function AvailabilitySidebar({ bloqueiosManuais, feriasMarcadas, periodos }) {
  return (
    <aside>
      <section className="card mb-16">
        <div className="card-header">
          <h2 className="card-title">Férias marcadas</h2>
          <StatusBadge tone={feriasMarcadas.length > 0 ? 'green' : 'gray'}>
            {feriasMarcadas.length}
          </StatusBadge>
        </div>
        <div className="card-body blocked-list">
          {feriasMarcadas.length ? feriasMarcadas.map(item => (
            <div className="vacation-item inline-start gap-8" key={item.id}>
              <span className="cal-detail-dot mt-3" style={{ background: item.cor || '#64748b' }} />
              <div>
                <strong>
                  {item.nome}
                  {item.ferias_acordo && <StatusBadge tone="blue">Por acordo</StatusBadge>}
                </strong>
                <div className="muted-xs">
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
              <div className="inline-center gap-6">
                <StatusBadge tone={bloqueio.tipo === 'recesso' ? 'blue' : 'red'}>
                  {bloqueio.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                </StatusBadge>
                <strong>{bloqueio.motivo}</strong>
              </div>
              <span className="muted-xs">
                {formatDate(bloqueio.data_inicio)} a {formatDate(bloqueio.data_fim)}
              </span>
            </div>
          )) : <p className="muted">Sem bloqueios cadastrados.</p>}

          <div className="divider" />
          <h3 className="text-sm-strong mb-10">Bloqueios por limite de equipe</h3>
          {periodos.length ? periodos.map((periodo, index) => (
            <div className="blocked-item" key={index}>
              <strong>{formatDate(periodo.data_inicio)} a {formatDate(periodo.data_fim)}</strong>
              <span className="muted-xs">Limite simultâneo atingido</span>
            </div>
          )) : <p className="muted">Sem datas bloqueadas por limite.</p>}
        </div>
      </section>
    </aside>
  )
}
