import { useEffect, useRef, useState } from 'react'
import LogsActions from '../components/logs/LogsActions'
import LogsTabela from '../components/logs/LogsTabela'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { exportLogs } from '../utils/logsExport'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Logs() {
  const toast = useToast()
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [importing, setImporting] = useState(false)
  const fileRef = useRef(null)

  const load = () => api.logs().then(setLogs)

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

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Logs do Sistema"
        subtitle="Auditoria das principais ações realizadas no sistema."
        action={
          <LogsActions
            fileRef={fileRef}
            importing={importing}
            logs={logs}
            onExport={() => exportLogs(logs)}
            onImport={handleImport}
          />
        }
      />

      <LogsTabela
        logs={filtered}
        search={search}
        onSearchChange={setSearch}
      />
    </>
  )
}
