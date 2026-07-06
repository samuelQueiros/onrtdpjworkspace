import { useMemo } from 'react'
import {
  buildMonthDays,
  findManualBlock,
  isBlockedByLimit,
  MONTHS,
  toIso,
  vacationsOnDay,
  WEEK_DAYS,
} from '../../utils/availabilityCalendar'

export default function MiniCalendar({ year, month, periodos, feriasMarcadas, bloqueiosManuais, selectedDay, onSelectDay }) {
  const days = useMemo(() => buildMonthDays(year, month), [year, month])
  const todayIso = toIso(new Date())

  return (
    <div className="mini-cal">
      <h4 className="mini-cal-title">{MONTHS[month]}</h4>
      <div className="cal-grid mini">
        {WEEK_DAYS.map((day, index) => <div className="cal-dow" key={index}>{day}</div>)}
        {days.map((date, index) => {
          if (!date) return <div className="cal-day empty" key={`e-${index}`} />

          const iso = toIso(date)
          const bloqueadoLimite = isBlockedByLimit(iso, periodos)
          const bloqueio = findManualBlock(iso, bloqueiosManuais)
          const dayVacs = vacationsOnDay(iso, feriasMarcadas)
          const isMarked = dayVacs.length > 0
          const isToday = iso === todayIso
          const isSelected = selectedDay === iso

          let className = 'cal-day '
          if (bloqueio) className += 'manual-block'
          else if (bloqueadoLimite) className += 'blocked'
          else if (isMarked) className += 'marked'
          else className += 'available'
          if (isToday) className += ' today'
          if (isSelected) className += ' selected'

          const tooltipParts = []
          if (bloqueio) tooltipParts.push(`${bloqueio.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}: ${bloqueio.motivo}`)
          dayVacs.forEach(vacation => tooltipParts.push(`${vacation.nome}`))

          return (
            <div
              className={className}
              key={iso}
              title={tooltipParts.join('\n')}
              onClick={() => onSelectDay(iso === selectedDay ? null : iso)}
            >
              <span className="cal-day-num">{date.getDate()}</span>
              {isMarked && !bloqueio && (
                <div className="cal-day-dots">
                  {dayVacs.slice(0, 2).map((vacation, dotIndex) => (
                    <span key={dotIndex} className="cal-user-dot" style={{ background: vacation.cor || '#64748b' }} />
                  ))}
                  {dayVacs.length > 2 && <span className="cal-user-dot-more">+{dayVacs.length - 2}</span>}
                </div>
              )}
              {bloqueio && <span className="cal-block-label">{bloqueio.tipo === 'recesso' ? 'R' : 'B'}</span>}
            </div>
          )
        })}
      </div>
    </div>
  )
}
