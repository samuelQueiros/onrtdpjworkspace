export const WEEK_DAYS = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']

export const MONTHS = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]

export function toIso(date) {
  return date.toISOString().slice(0, 10)
}

export function isBlockedByLimit(iso, periods) {
  return periods.some(period => iso >= period.data_inicio && iso <= period.data_fim)
}

export function findManualBlock(iso, bloqueios) {
  return bloqueios.find(bloqueio => iso >= bloqueio.data_inicio && iso <= bloqueio.data_fim)
}

export function vacationsOnDay(iso, vacations) {
  return vacations.filter(vacation => iso >= vacation.data_inicio && iso <= vacation.data_fim)
}

export function buildMonthDays(year, month) {
  const first = new Date(year, month, 1)
  const total = new Date(year, month + 1, 0).getDate()
  const blanks = Array.from({ length: first.getDay() }, () => null)
  const days = Array.from({ length: total }, (_, index) => new Date(year, month, index + 1))
  return [...blanks, ...days]
}
