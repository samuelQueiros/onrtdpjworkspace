import { formatDateTime } from './formatters'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

export function exportLogs(logs) {
  const rows = [
    ['Data', 'Ação', 'Usuário', 'E-mail', 'Detalhes'],
    ...logs.map(log => [
      formatDateTime(log.criado_em),
      log.acao,
      log.nome_usuario || `#${log.user_id}`,
      log.email_usuario || '',
      log.detalhes,
    ]),
  ]
  const csv = `sep=;\r\n${rows.map(row => row.map(csvCell).join(';')).join('\r\n')}`
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs-ferias-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
