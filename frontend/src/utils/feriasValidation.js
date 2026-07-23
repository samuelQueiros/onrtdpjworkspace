const NOMES_DIA = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']

export function overlaps(start, end, period) {
  return start <= period.data_fim && end >= period.data_inicio
}

function parseDate(str) {
  if (!str) return null
  const [year, month, day] = str.split('-').map(Number)
  return new Date(year, month - 1, day)
}

const DIAS_INICIO_PERMITIDOS = [0, 1, 2] // segunda, terça, quarta-feira

function feriadoBloqueante(inicio, feriadosSet) {
  for (const offset of [0, 1, 2]) {
    const candidato = new Date(inicio)
    candidato.setDate(inicio.getDate() + offset)
    const iso = candidato.toISOString().split('T')[0]
    if (feriadosSet.has(iso)) return { data: candidato, offset }
  }
  return null
}

export function validarDataInicio(dataInicio, dataFim, feriadosSet) {
  const hoje = new Date()
  hoje.setHours(0, 0, 0, 0)

  const inicio = parseDate(dataInicio)
  const fim = parseDate(dataFim)

  if (!inicio || !fim) return null

  if (fim < inicio) {
    return 'A data de fim não pode ser anterior à data de início.'
  }

  if (inicio < hoje) {
    return 'A data de início não pode ser anterior a hoje.'
  }

  const getDow = date => (date.getDay() + 6) % 7
  const dia = getDow(inicio)
  const permitidos = DIAS_INICIO_PERMITIDOS.map(day => NOMES_DIA[day])

  if (!DIAS_INICIO_PERMITIDOS.includes(dia)) {
    const motivo = dia >= 5
      ? 'dia de descanso semanal remunerado (DSR)'
      : 'as férias somente podem iniciar às segunda, terça ou quarta-feira'
    return `Férias não podem iniciar em ${NOMES_DIA[dia]}: ${motivo}. Dias permitidos: ${permitidos.join(', ')}.`
  }

  const resultado = feriadoBloqueante(inicio, feriadosSet)
  if (resultado) {
    const feriadoStr = resultado.data.toLocaleDateString('pt-BR')
    const motivo = resultado.offset === 0
      ? `é um feriado (${feriadoStr})`
      : `está nos dois dias imediatamente anteriores ao feriado de ${feriadoStr}`
    return `Férias não podem iniciar em ${NOMES_DIA[dia]}: ${motivo}. Dias permitidos: ${permitidos.join(', ')}.`
  }

  return null
}
