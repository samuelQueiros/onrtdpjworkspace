import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EditarFeriasModal from '../components/minhasFerias/EditarFeriasModal'
import ResumoFeriasCards from '../components/minhasFerias/ResumoFeriasCards'
import TabelaMinhasFerias from '../components/minhasFerias/TabelaMinhasFerias'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from './_helpers'

export default function MinhasFerias() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editando, setEditando] = useState(null)

  const load = () => api.minhasFerias().then(setData).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const ferias = data?.ferias || []
  const saldo = data?.saldo ?? user?.dias_restantes ?? 0

  const cancel = async id => {
    if (!confirm('Cancelar este período de férias?')) return
    setError('')
    try {
      await api.cancelarFerias(id)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Minhas Férias"
        subtitle="Histórico dos períodos registrados na sua conta."
        action={<Link className="btn btn-primary" to="/solicitar">Solicitar férias</Link>}
      />

      {error && <div className="alert alert-error spaced">{error}</div>}

      <ResumoFeriasCards data={data} saldo={saldo} />

      <TabelaMinhasFerias
        ferias={ferias}
        onCancel={cancel}
        onEdit={setEditando}
      />

      {editando && (
        <EditarFeriasModal
          ferias={editando}
          onClose={() => setEditando(null)}
          onSaved={() => { setEditando(null); load() }}
        />
      )}
    </>
  )
}
