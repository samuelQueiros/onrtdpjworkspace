import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import { LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

const DOW = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']
const MONTHS = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

function toIso(date) {
  return date.toISOString().slice(0, 10)
}

function isBlocked(iso, periods) {
  return periods.some(p => iso >= p.data_inicio && iso <= p.data_fim)
}

function bloqueioManual(iso, bloqueios) {
  return bloqueios.find(b => iso >= b.data_inicio && iso <= b.data_fim)
}

function vacationsOnDay(iso, vacations) {
  return vacations.filter(v => iso >= v.data_inicio && iso <= v.data_fim)
}

function buildMonthDays(year, month) {
  const first = new Date(year, month, 1)
  const total = new Date(year, month + 1, 0).getDate()
  const blanks = Array.from({ length: first.getDay() }, () => null)
  const days = Array.from({ length: total }, (_, i) => new Date(year, month, i + 1))
  return [...blanks, ...days]
}

function MiniCalendar({ year, month, periodos, feriasMarcadas, bloqueiosManuais, selectedDay, onSelectDay }) {
  const days = useMemo(() => buildMonthDays(year, month), [year, month])
  const todayIso = toIso(new Date())

  return (
    <div className="mini-cal">
      <h4 className="mini-cal-title">{MONTHS[month]}</h4>
      <div className="cal-grid mini">
        {DOW.map((d, i) => <div className="cal-dow" key={i}>{d}</div>)}
        {days.map((date, i) => {
          if (!date) return <div className="cal-day empty" key={`e-${i}`} />
          const iso = toIso(date)
          const bloqueadoLimite = isBlocked(iso, periodos)
          const bm = bloqueioManual(iso, bloqueiosManuais)
          const dayVacs = vacationsOnDay(iso, feriasMarcadas)
          const isMarked = dayVacs.length > 0
          const isToday = iso === todayIso
          const isSelected = selectedDay === iso

          let cls = 'cal-day '
          if (bm) cls += 'manual-block'
          else if (bloqueadoLimite) cls += 'blocked'
          else if (isMarked) cls += 'marked'
          else cls += 'available'
          if (isToday) cls += ' today'
          if (isSelected) cls += ' selected'

          const tooltipParts = []
          if (bm) tooltipParts.push(`${bm.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}: ${bm.motivo}`)
          dayVacs.forEach(v => tooltipParts.push(`${v.nome}`))

          return (
            <div
              className={cls}
              key={iso}
              title={tooltipParts.join('\n')}
              onClick={() => onSelectDay(iso === selectedDay ? null : iso)}
            >
              <span className="cal-day-num">{date.getDate()}</span>
              {isMarked && !bm && dayVacs.length > 0 && (
                <div className="cal-day-dots">
                  {dayVacs.slice(0, 2).map((v, idx) => (
                    <span key={idx} className="cal-user-dot" style={{ background: v.cor || '#64748b' }} />
                  ))}
                  {dayVacs.length > 2 && <span className="cal-user-dot-more">+{dayVacs.length - 2}</span>}
                </div>
              )}
              {bm && <span className="cal-block-label">{bm.tipo === 'recesso' ? 'R' : 'B'}</span>}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function Disponibilidade() {
  const [periodos, setPeriodos] = useState([])
  const [feriasMarcadas, setFeriasMarcadas] = useState([])
  const [bloqueiosManuais, setBloqueiosManuais] = useState([])
  const [year, setYear] = useState(new Date().getFullYear())
  const [loading, setLoading] = useState(true)
  const [selectedDay, setSelectedDay] = useState(null)

  useEffect(() => {
    api.disponibilidade()
      .then(data => {
        setPeriodos(data.periodos_bloqueados || [])
        setFeriasMarcadas(data.ferias_marcadas || [])
        setBloqueiosManuais(data.bloqueios_manuais || [])
      })
      .finally(() => setLoading(false))
  }, [])

  const selectedDayInfo = useMemo(() => {
    if (!selectedDay) return null
    return {
      bm: bloqueioManual(selectedDay, bloqueiosManuais),
      vacs: vacationsOnDay(selectedDay, feriasMarcadas),
    }
  }, [selectedDay, feriasMarcadas, bloqueiosManuais])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Disponibilidade"
        subtitle="Calendário anual de férias dos colaboradores. Clique em um dia para ver detalhes."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-body">

            {/* Navegação de ano */}
            <div className="cal-nav" style={{ marginBottom: 16 }}>
              <button className="btn btn-outline btn-sm" onClick={() => { setSelectedDay(null); setYear(y => y - 1) }}>← Anterior</button>
              <h3 className="cal-month-title">{year}</h3>
              <button className="btn btn-outline btn-sm" onClick={() => { setSelectedDay(null); setYear(y => y + 1) }}>Próximo →</button>
            </div>

            {/* Legenda */}
            <div className="cal-legend" style={{ marginBottom: 16 }}>
              <span className="cal-legend-item"><span className="cal-legend-dot available" />Disponível</span>
              <span className="cal-legend-item"><span className="cal-legend-dot marked" />Férias marcadas</span>
              <span className="cal-legend-item"><span className="cal-legend-dot blocked" />Limite atingido</span>
              <span className="cal-legend-item"><span className="cal-legend-dot manual-block" />Bloqueio/Recesso</span>
            </div>

            {/* Grade anual */}
            <div className="year-grid">
              {Array.from({ length: 12 }, (_, m) => (
                <MiniCalendar
                  key={m}
                  year={year}
                  month={m}
                  periodos={periodos}
                  feriasMarcadas={feriasMarcadas}
                  bloqueiosManuais={bloqueiosManuais}
                  selectedDay={selectedDay}
                  onSelectDay={setSelectedDay}
                />
              ))}
            </div>

            {/* Detalhe do dia selecionado */}
            {selectedDay && selectedDayInfo && (
              <div className="cal-detail-panel" style={{ marginTop: 16 }}>
                <div className="cal-detail-header">
                  <strong>
                    {new Date(`${selectedDay}T12:00:00`).toLocaleDateString('pt-BR', {
                      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
                    })}
                  </strong>
                  <button className="btn-close small" onClick={() => setSelectedDay(null)}>×</button>
                </div>
                {selectedDayInfo.bm && (
                  <div className={`cal-detail-block ${selectedDayInfo.bm.tipo}`}>
                    <strong>{selectedDayInfo.bm.tipo === 'recesso' ? '🏖 Recesso' : '🚫 Bloqueio'}</strong>: {selectedDayInfo.bm.motivo}
                  </div>
                )}
                {selectedDayInfo.vacs.length > 0 ? (
                  <ul className="cal-detail-list">
                    {selectedDayInfo.vacs.map(v => (
                      <li key={v.id} className="cal-detail-item">
                        <span className="cal-detail-dot" style={{ background: v.cor || '#64748b' }} />
                        <div>
                          <strong>{v.nome}</strong>
                          {v.ferias_acordo && <StatusBadge tone="blue" style={{ marginLeft: 6 }}>Por acordo</StatusBadge>}
                          <div className="muted" style={{ fontSize: 12 }}>
                            {formatDate(v.data_inicio)} a {formatDate(v.data_fim)} — {v.dias_usados} dia(s)
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : !selectedDayInfo.bm ? (
                  <p className="muted" style={{ fontSize: 13, marginTop: 8 }}>Nenhuma féria marcada neste dia.</p>
                ) : null}
              </div>
            )}
          </div>
        </section>

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
                      {item.ferias_acordo && <StatusBadge tone="blue" style={{ marginLeft: 6 }}>Por acordo</StatusBadge>}
                    </strong>
                    <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                      {formatDate(item.data_inicio)} a {formatDate(item.data_fim)} — {item.dias_usados} dia(s)
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
              {bloqueiosManuais.length ? bloqueiosManuais.map(b => (
                <div className="blocked-item" key={b.id}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <StatusBadge tone={b.tipo === 'recesso' ? 'blue' : 'red'}>
                      {b.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}
                    </StatusBadge>
                    <strong>{b.motivo}</strong>
                  </div>
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>
                    {formatDate(b.data_inicio)} a {formatDate(b.data_fim)}
                  </span>
                </div>
              )) : <p className="muted">Sem bloqueios cadastrados.</p>}

              <div className="divider" />
              <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Bloqueios por limite de equipe</h3>
              {periodos.length ? periodos.map((p, i) => (
                <div className="blocked-item" key={i}>
                  <strong>{formatDate(p.data_inicio)} a {formatDate(p.data_fim)}</strong>
                  <span style={{ fontSize: 12, color: 'var(--muted)' }}>Limite simultâneo atingido</span>
                </div>
              )) : <p className="muted">Sem datas bloqueadas por limite.</p>}
            </div>
          </section>
        </aside>
      </div>
    </>
  )
}
