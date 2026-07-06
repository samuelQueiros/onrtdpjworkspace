import MiniCalendar from './MiniCalendar'
import SelectedDayDetails from './SelectedDayDetails'

export default function AvailabilityCalendar({
  bloqueiosManuais,
  feriasMarcadas,
  onChangeYear,
  onSelectDay,
  periodos,
  selectedDay,
  selectedDayInfo,
  year,
}) {
  return (
    <section className="card">
      <div className="card-body">
        <div className="cal-nav" style={{ marginBottom: 16 }}>
          <button className="btn btn-outline btn-sm" onClick={() => onChangeYear(-1)}>← Anterior</button>
          <h3 className="cal-month-title">{year}</h3>
          <button className="btn btn-outline btn-sm" onClick={() => onChangeYear(1)}>Próximo →</button>
        </div>

        <div className="cal-legend" style={{ marginBottom: 16 }}>
          <span className="cal-legend-item"><span className="cal-legend-dot available" />Disponível</span>
          <span className="cal-legend-item"><span className="cal-legend-dot marked" />Férias marcadas</span>
          <span className="cal-legend-item"><span className="cal-legend-dot blocked" />Limite atingido</span>
          <span className="cal-legend-item"><span className="cal-legend-dot manual-block" />Bloqueio/Recesso</span>
        </div>

        <div className="year-grid">
          {Array.from({ length: 12 }, (_, month) => (
            <MiniCalendar
              key={month}
              year={year}
              month={month}
              periodos={periodos}
              feriasMarcadas={feriasMarcadas}
              bloqueiosManuais={bloqueiosManuais}
              selectedDay={selectedDay}
              onSelectDay={onSelectDay}
            />
          ))}
        </div>

        <SelectedDayDetails
          selectedDay={selectedDay}
          selectedDayInfo={selectedDayInfo}
          onClose={() => onSelectDay(null)}
        />
      </div>
    </section>
  )
}
