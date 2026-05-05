import { useEffect, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, formatDateTime } from './_helpers'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

function exportLogs(logs) {
  const rows = [
    ['Data', 'Acao', 'Usuario', 'Detalhes'],
    ...logs.map(log => [formatDateTime(log.criado_em), log.acao, `#${log.user_id}`, log.detalhes]),
  ]
  const csv = `sep=;\r\n${rows.map(row => row.map(csvCell).join(';')).join('\r\n')}`
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `logs-ferias-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.logs().then(setLogs).finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Logs do Sistema"
        subtitle="Auditoria das principais acoes realizadas no sistema."
        action={<button className="btn btn-primary" onClick={() => exportLogs(logs)} disabled={!logs.length}>Exportar Excel</button>}
      />
      <section className="card">
        <div className="table-wrap">
          {logs.length ? (
            <table>
              <thead><tr><th>Data</th><th>Acao</th><th>Usuario</th><th>Detalhes</th></tr></thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id}>
                    <td>{formatDateTime(log.criado_em)}</td>
                    <td>{log.acao}</td>
                    <td>#{log.user_id}</td>
                    <td>{log.detalhes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <EmptyState title="Sem logs" text="As acoes administrativas aparecerao aqui." />}
        </div>
      </section>
    </>
  )
}
