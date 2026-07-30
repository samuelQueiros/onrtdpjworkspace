import { formatDate } from '../../utils/formatters'
import { EmptyState } from './PageHelpers'

export default function Timeline({ eventos }) {
  if (!eventos?.length) {
    return <EmptyState title="Sem eventos registrados" text="O histórico do colaborador aparecerá aqui." />
  }

  return (
    <ol className="timeline">
      {eventos.map((evento, index) => (
        <li key={`${evento.titulo}-${evento.data}-${index}`} className="timeline-item">
          <span className={`timeline-dot timeline-dot-${evento.tipo || 'padrao'}`} aria-hidden="true" />
          <div className="timeline-content">
            <div className="timeline-header">
              <strong>{evento.titulo}</strong>
              <span className="muted">{formatDate(evento.data)}</span>
            </div>
            {evento.descricao && <p className="muted timeline-descricao">{evento.descricao}</p>}
          </div>
        </li>
      ))}
    </ol>
  )
}
