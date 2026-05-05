import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, formatDate } from './_helpers'

const DOW = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']

function toIso(date) {
  return date.toISOString().slice(0, 10)
}

function blocked(iso, periods) {
  return periods.some(period => iso >= period.data_inicio && iso <= period.data_fim)
}

function vacationsOnDay(iso, vacations) {
  return vacations.filter(item => iso >= item.data_inicio && iso <= item.data_fim)
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
    const monthDays = Array.from({ length: total }, (_, index) => new Date(year, month, index + 1))
    return [...blanks, ...monthDays]
  }, [cursor])

  const changeMonth = amount => setCursor(current => new Date(current.getFullYear(), current.getMonth() + amount, 1))

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader title="Disponibilidade" subtitle="Todos os usuarios visualizam as ferias marcadas. Azul indica ferias agendadas; vermelho indica limite simultaneo atingido." />

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-body">
            <div className="cal-nav">
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(-1)}>Anterior</button>
              <h3>{cursor.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}</h3>
              <button className="btn btn-outline btn-sm" onClick={() => changeMonth(1)}>Proximo</button>
            </div>
            <div className="cal-grid">
              {DOW.map(day => <div className="cal-dow" key={day}>{day}</div>)}
              {days.map((date, index) => {
                if (!date) return <div className="cal-day empty" key={`empty-${index}`} />
                const iso = toIso(date)
                const isBlocked = blocked(iso, periodos)
                const dayVacations = vacationsOnDay(iso, feriasMarcadas)
                const isMarked = dayVacations.length > 0
                const isToday = iso === toIso(new Date())
                return (
                  <div
                    className={`cal-day ${isBlocked ? 'blocked' : isMarked ? 'marked' : 'available'}${isToday ? ' today' : ''}`}
                    key={iso}
                    title={dayVacations.map(item => `${item.nome}: ${formatDate(item.data_inicio)} a ${formatDate(item.data_fim)}`).join('\n')}
                  >
                    <span>{date.getDate()}</span>
                    {isMarked && <small>{dayVacations.length}</small>}
                  </div>
                )
              })}
            </div>
          </div>
        </section>

        <aside className="card">
          <div className="card-header"><h2 className="card-title">Ferias marcadas</h2></div>
          <div className="card-body blocked-list">
            {feriasMarcadas.length ? feriasMarcadas.map(item => (
              <div className="vacation-item" key={item.id}>
                <strong>{item.nome}</strong>
                <span>{formatDate(item.data_inicio)} a {formatDate(item.data_fim)} - {item.dias_usados} dia(s)</span>
              </div>
            )) : <p className="muted">Sem ferias marcadas no calendario.</p>}

            <div className="divider" />
            <h2 className="card-title">Bloqueios por limite</h2>
            {periodos.length ? periodos.map((periodo, index) => (
              <div className="blocked-item" key={index}>
                <strong>{formatDate(periodo.data_inicio)} a {formatDate(periodo.data_fim)}</strong>
                <span>Indisponivel para novas solicitacoes</span>
              </div>
            )) : <p className="muted">Sem datas bloqueadas.</p>}
          </div>
        </aside>
      </div>
    </>
  )
}
