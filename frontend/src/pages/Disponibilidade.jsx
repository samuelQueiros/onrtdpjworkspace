import { useEffect, useMemo, useState } from 'react'
import AvailabilityCalendar from '../components/availability/AvailabilityCalendar'
import AvailabilitySidebar from '../components/availability/AvailabilitySidebar'
import { findManualBlock, vacationsOnDay } from '../utils/availabilityCalendar'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from './_helpers'

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
      bm: findManualBlock(selectedDay, bloqueiosManuais),
      vacs: vacationsOnDay(selectedDay, feriasMarcadas),
    }
  }, [selectedDay, feriasMarcadas, bloqueiosManuais])

  const changeYear = delta => {
    setSelectedDay(null)
    setYear(currentYear => currentYear + delta)
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Disponibilidade"
        subtitle="Calendário anual de férias dos colaboradores. Clique em um dia para ver detalhes."
      />

      <div className="grid-2 grid-2-wide-left">
        <AvailabilityCalendar
          bloqueiosManuais={bloqueiosManuais}
          feriasMarcadas={feriasMarcadas}
          onChangeYear={changeYear}
          onSelectDay={setSelectedDay}
          periodos={periodos}
          selectedDay={selectedDay}
          selectedDayInfo={selectedDayInfo}
          year={year}
        />

        <AvailabilitySidebar
          bloqueiosManuais={bloqueiosManuais}
          feriasMarcadas={feriasMarcadas}
          periodos={periodos}
        />
      </div>
    </>
  )
}
