import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

const DOW = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

function toIso(date) {
  return date.toISOString().slice(0, 10)
}

function blocked(iso, periods) {
  return periods.some(p => iso >= p.data_inicio && iso <= p.data_fim)
}

function vacationsOnDay(iso, vacations) {
  return vacations.filter(v => iso >= v.data_inicio && iso <= v.data_fim)
}

export default function Disponibilidade() {
  const [periodos, setPeriodos] = useState([])
  const [feriasMarcadas, setFeriasMarcadas] = useState([])
  const [cursor, setCursor] = useState(new Date())
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.disponibilidade()
      .then(data => {
        setPeriodos(data.periodos_bloqueados || [])
        setFeriasMarcadas(data.ferias_marcadas || [])
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

  const changeMonth = n => setCursor(c => new Date(c.getFullYear(), c.getMonth() + n, 1))

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Disponibilidade"
        subtitle="Férias marcadas de todos os colaboradores. Azul = férias agendadas; vermelho = limite simultâneo atingido."
      />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-body">
            <div className="cal-nav">
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(-1)}>Anterior</button>
              <h3>{cursor.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</h3>
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(1)}>Próximo</button>
            </div>
            <div className="cal-grid">
              {DOW.map(d => <div className="cal-dow" key={d}>{d}</div>)}
              {days.map((date, i) => {
                if (!date) return <div className="cal-day empty" key={`e-${i}`} />
                const iso = toIso(date)
                const isBlocked = blocked(iso, periodos)
                const dayVacs = vacationsOnDay(iso, feriasMarcadas)
                const isMarked = dayVacs.length > 0
                const isToday = iso === toIso(new Date())
                return (
                  <div
                    className={`cal-day ${isBlocked ? 'blocked' : isMarked ? 'marked' : 'available'}${isToday ? ' today' : ''}`}
                    key={iso}
                    title={dayVacs.map(v => `${v.nome}: ${formatDate(v.data_inicio)} a ${formatDate(v.data_fim)}${v.ferias_acordo ? ' (acordo)' : ''}`).join('\n')}
                  >
                    <span>{date.getDate()}</span>
                    {isMarked && <small>{dayVacs.length}</small>}
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        <aside className="card">
          <div className="card-header"><h2 className="card-title">Férias marcadas</h2></div>
          <div className="card-body blocked-list">
            {feriasMarcadas.length ? feriasMarcadas.map(item => (
              <div className="vacation-item" key={item.id}>
                <strong>
                  {item.nome}
                  {item.ferias_acordo && <StatusBadge tone="blue" style={{ marginLeft: 6 }}>Por acordo</StatusBadge>}
                </strong>
                <span>{formatDate(item.data_inicio)} a {formatDate(item.data_fim)} — {item.dias_usados} dia(s)</span>
              </div>
            )) : <p className="muted">Sem férias marcadas no calendário.</p>}

            <div className="divider" />
            <h2 className="card-title" style={{ marginBottom: 10 }}>Bloqueios por limite</h2>
            {periodos.length ? periodos.map((p, i) => (
              <div className="blocked-item" key={i}>
                <strong>{formatDate(p.data_inicio)} a {formatDate(p.data_fim)}</strong>
                <span>Indisponível para novas solicitações</span>
              </div>
            )) : <p className="muted">Sem datas bloqueadas.</p>}
          </div>
        </aside>
      </div>
    </>
  )
}
