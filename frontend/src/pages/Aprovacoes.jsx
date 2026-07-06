import { useEffect, useState } from 'react'
import FiltrosAprovacoes from '../components/aprovacoes/FiltrosAprovacoes'
import RejeitarFeriasModal from '../components/aprovacoes/RejeitarFeriasModal'
import TabelaAprovacoes from '../components/aprovacoes/TabelaAprovacoes'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Aprovacoes() {
  const [todas, setTodas] = useState([])
  const [loading, setLoading] = useState(true)
  const [rejeitando, setRejeitando] = useState(null)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')
  const [filtro, setFiltro] = useState('pendente')

  const load = () =>
    api.todasFerias()
      .then(setTodas)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const aprovar = async id => {
    setMsg('')
    setError('')
    try {
      await api.aprovarFerias(id)
      setMsg('Férias aprovadas com sucesso.')
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const filtradas = todas.filter(ferias =>
    filtro === 'todas' ? true : ferias.status === filtro
  )

  const counts = {
    pendente: todas.filter(ferias => ferias.status === 'pendente').length,
    aprovada: todas.filter(ferias => ferias.status === 'aprovada').length,
    rejeitada: todas.filter(ferias => ferias.status === 'rejeitada').length,
    todas: todas.length,
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Aprovação de Férias"
        subtitle="Gerencie todas as solicitações de férias: pendentes, aprovadas e rejeitadas."
      />

      {msg && <div className="alert alert-success spaced">{msg}</div>}
      {error && <div className="alert alert-error spaced">{error}</div>}

      <FiltrosAprovacoes counts={counts} filtro={filtro} onChange={setFiltro} />

      <TabelaAprovacoes
        filtro={filtro}
        ferias={filtradas}
        onAprovar={aprovar}
        onRejeitar={setRejeitando}
      />

      {rejeitando && (
        <RejeitarFeriasModal
          ferias={rejeitando}
          onClose={() => setRejeitando(null)}
          onRejeitado={() => { setRejeitando(null); setMsg('Férias rejeitadas.'); load() }}
        />
      )}
    </>
  )
}
