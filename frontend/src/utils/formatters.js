export function formatDate(value) {
  if (!value) return '-'
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return '-'
  return `${day.padStart(2, '0')}/${month.padStart(2, '0')}/${year}`
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  const data = formatDate(date.toISOString().slice(0, 10))
  const hora = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  return `${data} ${hora}`
}

export function calcDays(start, end) {
  if (!start || !end) return 0
  const a = new Date(`${start}T12:00:00`)
  const b = new Date(`${end}T12:00:00`)
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime()) || b < a) return 0
  return Math.floor((b - a) / 86400000) + 1
}

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
