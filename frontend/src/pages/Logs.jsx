import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, formatDateTime } from './_helpers'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

function exportLogs(logs) {
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
  const blob = new Blob([`﻿${csv}`], { type: 'text/csv;charset=utf-8;' })
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
  const [search, setSearch] = useState('')
  const [importing, setImporting] = useState(false)
  const [importMsg, setImportMsg] = useState('')
  const fileRef = useRef(null)

  useEffect(() => {
    api.logs().then(setLogs).finally(() => setLoading(false))
  }, [])

  const filtered = logs.filter(l =>
    !search ||
    (l.nome_usuario || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.acao || '').toLowerCase().includes(search.toLowerCase()) ||
    (l.detalhes || '').toLowerCase().includes(search.toLowerCase())
  )

  const handleImport = async e => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setImportMsg('')
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await api.importarLogs(fd)
      setImportMsg(res.mensagem)
      if (res.inseridos > 0) {
        api.logs().then(setLogs)
      }
    } catch (err) {
      setImportMsg(`Erro: ${err.message}`)
    } finally {
      setImporting(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Logs do Sistema"
        subtitle="Auditoria das principais ações realizadas no sistema."
        action={
          <div className="button-row">
            <label className="btn btn-outline" style={{ cursor: 'pointer' }}>
              {importing ? 'Importando...' : 'Importar Excel'}
              <input ref={fileRef} type="file" accept=".xlsx,.xls" style={{ display: 'none' }} onChange={handleImport} disabled={importing} />
            </label>
            <button className="btn btn-primary" onClick={() => exportLogs(logs)} disabled={!logs.length}>
              Exportar Excel
            </button>
          </div>
        }
      />

      {importMsg && (
        <div className={`alert spaced ${importMsg.startsWith('Erro') ? 'alert-error' : 'alert-success'}`}>
          {importMsg}
        </div>
      )}

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Registros ({filtered.length})</h2>
          <input
            className="search-input"
            placeholder="Filtrar por usuário, ação ou detalhe..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="table-wrap">
          {filtered.length ? (
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Ação</th>
                  <th>Usuário</th>
                  <th>E-mail</th>
                  <th>Detalhes</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(log => (
                  <tr key={log.id}>
                    <td className="nowrap">{formatDateTime(log.criado_em)}</td>
                    <td><code className="action-code">{log.acao}</code></td>
                    <td>{log.nome_usuario || `#${log.user_id}`}</td>
                    <td className="muted">{log.email_usuario || '—'}</td>
                    <td>{log.detalhes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <EmptyState title="Sem logs" text="As ações administrativas aparecerão aqui." />
          )}
        </div>
      </section>
    </>
  )
}
