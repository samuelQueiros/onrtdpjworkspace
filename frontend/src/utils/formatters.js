export function formatDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return '-'
  return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'America/Sao_Paulo',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function calcDays(start, end) {
  if (!start || !end) return 0
  const a = new Date(`${start}T12:00:00`)
  const b = new Date(`${end}T12:00:00`)
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime()) || b < a) return 0
  return Math.floor((b - a) / 86400000) + 1
}

export function calcularTempoDeEmpresa(dataAdmissao) {
  if (!dataAdmissao) return '-'
  const inicio = new Date(`${String(dataAdmissao).slice(0, 10)}T12:00:00`)
  if (Number.isNaN(inicio.getTime())) return '-'

  const hoje = new Date()
  let anos = hoje.getFullYear() - inicio.getFullYear()
  let meses = hoje.getMonth() - inicio.getMonth()
  if (hoje.getDate() < inicio.getDate()) meses -= 1
  if (meses < 0) {
    anos -= 1
    meses += 12
  }
  if (anos < 0) return '-'

  const partes = []
  if (anos > 0) partes.push(`${anos} ano${anos > 1 ? 's' : ''}`)
  if (meses > 0) partes.push(`${meses} ${meses > 1 ? 'meses' : 'mês'}`)
  return partes.length ? partes.join(' e ') : 'Menos de 1 mês'
}

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
