import { useEffect, useState } from 'react'
import '../styles/pages/aprovacoes.css'
import FiltrosAprovacoes from '../components/aprovacoes/FiltrosAprovacoes'
import RejeitarFeriasModal from '../components/aprovacoes/RejeitarFeriasModal'
import TabelaAprovacoes from '../components/aprovacoes/TabelaAprovacoes'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Aprovacoes() {
  const toast = useToast()
  const [todas, setTodas] = useState([])
  const [loading, setLoading] = useState(true)
  const [rejeitando, setRejeitando] = useState(null)
  const [filtro, setFiltro] = useState('pendente')

  const load = () =>
    api.todasFerias()
      .then(setTodas)
      .finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const aprovar = async id => {
    try {
      await api.aprovarFerias(id)
      toast.success('Férias aprovadas com sucesso.')
      await load()
    } catch (err) {
      toast.error(err.message)
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
          onRejeitado={() => { setRejeitando(null); toast.success('Férias rejeitadas.'); load() }}
        />
      )}
    </>
  )
}
