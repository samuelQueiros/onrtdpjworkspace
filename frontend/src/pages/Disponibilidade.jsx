import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

const DOW = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

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

function getContrastColor(hex) {
  if (!hex) return '#fff'
  const c = hex.replace('#', '')
  const r = parseInt(c.substring(0, 2), 16)
  const g = parseInt(c.substring(2, 4), 16)
  const b = parseInt(c.substring(4, 6), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#1e293b' : '#ffffff'
}

export default function Disponibilidade() {
  const [periodos, setPeriodos] = useState([])
  const [feriasMarcadas, setFeriasMarcadas] = useState([])
  const [bloqueiosManuais, setBloqueiosManuais] = useState([])
  const [cursor, setCursor] = useState(new Date())
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

  const days = useMemo(() => {
    const year = cursor.getFullYear()
    const month = cursor.getMonth()
    const first = new Date(year, month, 1)
    const total = new Date(year, month + 1, 0).getDate()
    const blanks = Array.from({ length: first.getDay() }, () => null)
    const monthDays = Array.from({ length: total }, (_, i) => new Date(year, month, i + 1))
    return [...blanks, ...monthDays]
  }, [cursor])

  const changeMonth = n => {
    setSelectedDay(null)
    setCursor(c => new Date(c.getFullYear(), c.getMonth() + n, 1))
  }

  const selectedDayVacs = useMemo(() => {
    if (!selectedDay) return []
    return vacationsOnDay(selectedDay, feriasMarcadas)
  }, [selectedDay, feriasMarcadas])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Disponibilidade"
        subtitle="Calendário de férias dos colaboradores. Clique em um dia para ver detalhes."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-body">
            <div className="cal-nav">
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(-1)}>← Anterior</button>
              <h3 className="cal-month-title">
                {cursor.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
              </h3>
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(1)}>Próximo →</button>
            </div>

            {/* Legenda */}
            <div className="cal-legend">
              <span className="cal-legend-item"><span className="cal-legend-dot available" />Disponível</span>
              <span className="cal-legend-item"><span className="cal-legend-dot marked" />Férias marcadas</span>
              <span className="cal-legend-item"><span className="cal-legend-dot blocked" />Limite atingido</span>
              <span className="cal-legend-item"><span className="cal-legend-dot manual-block" />Bloqueio/Recesso</span>
            </div>

            <div className="cal-grid">
              {DOW.map(d => <div className="cal-dow" key={d}>{d}</div>)}
              {days.map((date, i) => {
                if (!date) return <div className="cal-day empty" key={`e-${i}`} />
                const iso = toIso(date)
                const bloqueadoLimite = isBlocked(iso, periodos)
                const bloqueadoManual = bloqueioManual(iso, bloqueiosManuais)
                const dayVacs = vacationsOnDay(iso, feriasMarcadas)
                const isMarked = dayVacs.length > 0
                const isToday = iso === toIso(new Date())
                const isSelected = selectedDay === iso

                let className = 'cal-day '
                if (bloqueadoManual) className += 'manual-block'
                else if (bloqueadoLimite) className += 'blocked'
                else if (isMarked) className += 'marked'
                else className += 'available'
                if (isToday) className += ' today'
                if (isSelected) className += ' selected'

                const tooltipParts = []
                if (bloqueadoManual) tooltipParts.push(`${bloqueadoManual.tipo === 'recesso' ? 'Recesso' : 'Bloqueio'}: ${bloqueadoManual.motivo}`)
                dayVacs.forEach(v => tooltipParts.push(`${v.nome}: ${formatDate(v.data_inicio)} a ${formatDate(v.data_fim)}`))

                return (
                  <div
                    className={className}
                    key={iso}
                    title={tooltipParts.join('\n')}
                    onClick={() => setSelectedDay(iso === selectedDay ? null : iso)}
                  >
                    <span className="cal-day-num">{date.getDate()}</span>
                    {isMarked && !bloqueadoManual && (
                      <div className="cal-day-dots">
                        {dayVacs.slice(0, 3).map((v, idx) => (
                          <span
                            key={idx}
                            className="cal-user-dot"
                            style={{ background: v.cor || '#64748b' }}
                            title={v.nome}
                          />
                        ))}
                        {dayVacs.length > 3 && <span className="cal-user-dot-more">+{dayVacs.length - 3}</span>}
                      </div>
                    )}
                    {bloqueadoManual && (
                      <span className="cal-block-label">
                        {bloqueadoManual.tipo === 'recesso' ? 'R' : 'B'}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Detalhe do dia selecionado */}
            {selectedDay && (
              <div className="cal-detail-panel">
                <div className="cal-detail-header">
                  <strong>
                    {new Date(`${selectedDay}T12:00:00`).toLocaleDateString('pt-BR', {
                      weekday: 'long', day: 'numeric', month: 'long'
                    })}
                  </strong>
                  <button className="btn-close small" onClick={() => setSelectedDay(null)}>×</button>
                </div>
                {(() => {
                  const bm = bloqueioManual(selectedDay, bloqueiosManuais)
                  const vacs = vacationsOnDay(selectedDay, feriasMarcadas)
                  return (
                    <>
                      {bm && (
                        <div className={`cal-detail-block ${bm.tipo}`}>
                          <strong>{bm.tipo === 'recesso' ? '🏖 Recesso' : '🚫 Bloqueio'}</strong>: {bm.motivo}
                        </div>
                      )}
                      {vacs.length > 0 ? (
                        <ul className="cal-detail-list">
                          {vacs.map(v => (
                            <li key={v.id} className="cal-detail-item">
                              <span
                                className="cal-detail-dot"
                                style={{ background: v.cor || '#64748b' }}
                              />
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
                      ) : !bm ? (
                        <p className="muted" style={{ fontSize: 13, marginTop: 8 }}>Nenhuma féria marcada neste dia.</p>
                      ) : null}
                    </>
                  )
                })()}
              </div>
            )}
          </div>
        </section>

        <aside>
          {/* Férias marcadas */}
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
                  <span
                    style={{
                      width: 12, height: 12, borderRadius: '50%',
                      background: item.cor || '#64748b', flexShrink: 0, marginTop: 3
                    }}
                  />
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

          {/* Bloqueios manuais */}
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
