const NOMES_DIA = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']

export function overlaps(start, end, period) {
  return start <= period.data_fim && end >= period.data_inicio
}

function parseDate(str) {
  if (!str) return null
  const [year, month, day] = str.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function primeiroDiaDescansoNaSemana(ref, feriadosSet) {
  const segunda = new Date(ref)
  segunda.setDate(ref.getDate() - ref.getDay() + (ref.getDay() === 0 ? -6 : 1))

  for (let delta = 0; delta < 5; delta++) {
    const dia = new Date(segunda)
    dia.setDate(segunda.getDate() + delta)
    const iso = dia.toISOString().split('T')[0]
    if (feriadosSet.has(iso)) return delta
  }

  return 5
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

  if (dia >= 5) {
    return `Férias não podem iniciar em ${NOMES_DIA[dia]} (dia de descanso).`
  }

  const limite = primeiroDiaDescansoNaSemana(inicio, feriadosSet)
  const bloqueados = new Set(
    [limite - 2, limite - 1, limite].filter(day => day >= 0 && day <= 4)
  )

  if (!bloqueados.has(dia)) return null

  const permitidos = [0, 1, 2, 3, 4].filter(day => !bloqueados.has(day)).map(day => NOMES_DIA[day])

  if (limite < 5) {
    const segunda = new Date(inicio)
    segunda.setDate(inicio.getDate() - getDow(inicio))
    const feriadoDia = new Date(segunda)
    feriadoDia.setDate(segunda.getDate() + limite)
    const feriadoStr = feriadoDia.toLocaleDateString('pt-BR')
    const motivo = `há um feriado em ${NOMES_DIA[limite]} (${feriadoStr}) nesta semana, antecipando o período de descanso`
    const sufixo = permitidos.length
      ? ` Dias permitidos nesta semana: ${permitidos.join(', ')}.`
      : ' Não há dia de início permitido nesta semana.'
    return `Férias não podem iniciar em ${NOMES_DIA[dia]}: ${motivo}.${sufixo}`
  }

  return `Férias não podem iniciar em ${NOMES_DIA[dia]}: está a menos de 48 horas do descanso semanal (sábado). Dias permitidos: ${permitidos.join(', ')}.`
}
