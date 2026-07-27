import { useEffect, useRef, useState } from 'react'
import '../styles/pages/logs.css'
import LogsActions from '../components/logs/LogsActions'
import LogsTabela from '../components/logs/LogsTabela'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Logs() {
  const toast = useToast()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [importing, setImporting] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 50
  const fileRef = useRef(null)

  const load = (targetPage = page) => api.logs(targetPage, pageSize).then(data => {
    setLogs(data.items)
    setTotal(data.total)
    setPage(data.page)
  })

  useEffect(() => {
    load().finally(() => setLoading(false))
  }, [])

  const filtered = logs.filter(log =>
    !search ||
    (log.nome_usuario || '').toLowerCase().includes(search.toLowerCase()) ||
    (log.acao || '').toLowerCase().includes(search.toLowerCase()) ||
    (log.detalhes || '').toLowerCase().includes(search.toLowerCase())
  )

  const handleImport = async event => {
    const file = event.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.importarLogs(formData)
      toast.success(res.mensagem)
      if (res.inseridos > 0) await load()
    } catch (err) {
      toast.error(err.message)
    } finally {
      setImporting(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const blob = await api.exportarLogs()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `logs-sistema-${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
      toast.success('Planilha de logs exportada com sucesso.')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setExporting(false)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Logs do Sistema"
        subtitle="Auditoria das principais ações realizadas no sistema."
        action={
          <LogsActions
            fileRef={fileRef}
            exporting={exporting}
            importing={importing}
            logs={logs}
            onExport={handleExport}
            onImport={handleImport}
          />
        }
      />

      <LogsTabela
        logs={filtered}
        search={search}
        onSearchChange={setSearch}
      />
      <div className="pagination-bar">
        <span>Página {page} de {Math.max(1, Math.ceil(total / pageSize))} · {total} registro(s)</span>
        <div className="button-row">
          <button className="btn btn-outline btn-sm" disabled={page <= 1} onClick={() => load(page - 1)}>Anterior</button>
          <button className="btn btn-outline btn-sm" disabled={page * pageSize >= total} onClick={() => load(page + 1)}>Próxima</button>
        </div>
      </div>
    </>
  )
}
