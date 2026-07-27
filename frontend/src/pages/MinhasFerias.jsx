import { useEffect, useState } from 'react'
import '../styles/pages/minhas-ferias.css'
import { Link } from 'react-router-dom'
import EditarFeriasModal from '../components/minhasFerias/EditarFeriasModal'
import ExtratoSaldoFerias from '../components/minhasFerias/ExtratoSaldoFerias'
import ResumoFeriasCards from '../components/minhasFerias/ResumoFeriasCards'
import TabelaMinhasFerias from '../components/minhasFerias/TabelaMinhasFerias'
import { useAuth } from '../contexts/AuthContext'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function MinhasFerias() {
  const { user } = useAuth()
  const confirmar = useConfirm()
  const toast = useToast()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editando, setEditando] = useState(null)

  const load = () => api.minhasFerias().then(setData).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const ferias = data?.ferias || []
  const saldo = data?.saldo ?? user?.dias_restantes ?? 0

  const cancel = async id => {
    const confirmado = await confirmar({
      title: 'Cancelar férias?',
      message: 'O período será removido da sua lista de férias registradas.',
      confirmLabel: 'Cancelar férias',
    })
    if (!confirmado) return

    try {
      await api.cancelarFerias(id)
      toast.success('Período de férias cancelado.')
      window.dispatchEvent(new Event('approvals:changed'))
      await load()
    } catch (err) {
      toast.error(err.message)
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

      <ResumoFeriasCards data={data} saldo={saldo} />

      <div className="minhas-ferias-sections">
        <ExtratoSaldoFerias movimentos={data?.movimentos_saldo} />

        <TabelaMinhasFerias
          ferias={ferias}
          onCancel={cancel}
          onEdit={setEditando}
        />
      </div>

      {editando && (
        <EditarFeriasModal
          ferias={editando}
          onClose={() => setEditando(null)}
          onSaved={() => { setEditando(null); toast.success('Férias atualizadas.'); load() }}
        />
      )}
    </>
  )
}
