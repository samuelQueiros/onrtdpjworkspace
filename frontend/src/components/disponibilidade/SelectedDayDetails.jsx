import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'

export default function SelectedDayDetails({ selectedDay, selectedDayInfo, onClose }) {
  if (!selectedDay || !selectedDayInfo) return null

  return (
    <div className="cal-detail-panel" style={{ marginTop: 16 }}>
      <div className="cal-detail-header">
        <strong>
          {new Date(`${selectedDay}T12:00:00`).toLocaleDateString('pt-BR', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
          })}
        </strong>
        <button className="btn-close small" onClick={onClose}>×</button>
      </div>

      {selectedDayInfo.bm && (
        <div className={`cal-detail-block ${selectedDayInfo.bm.tipo}`}>
          <strong>{selectedDayInfo.bm.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}</strong>: {selectedDayInfo.bm.motivo}
        </div>
      )}

      {selectedDayInfo.vacs.length > 0 ? (
        <ul className="cal-detail-list">
          {selectedDayInfo.vacs.map(vacation => (
            <li key={vacation.id} className="cal-detail-item">
              <span className="cal-detail-dot" style={{ background: vacation.cor || '#64748b' }} />
              <div>
                <strong>{vacation.nome}</strong>
                {vacation.ferias_acordo && <StatusBadge tone="blue">Por acordo</StatusBadge>}
                <div className="muted" style={{ fontSize: 12 }}>
                  {formatDate(vacation.data_inicio)} a {formatDate(vacation.data_fim)} - {vacation.dias_usados} dia(s)
                </div>
              </div>
            </li>
          ))}
        </ul>
      ) : !selectedDayInfo.bm ? (
        <p className="muted" style={{ fontSize: 13, marginTop: 8 }}>Nenhum período de férias marcado neste dia.</p>
      ) : null}
    </div>
  )
}
