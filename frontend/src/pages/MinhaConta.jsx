import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/minha-conta.css'
import MinhaContaDetalhes from '../components/minhaConta/MinhaContaDetalhes'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'

export default function MinhaConta() {
  const toast = useToast()
  const [perfil, setPerfil] = useState(null)
  const [ficha, setFicha] = useState(null)
  const [ferias, setFerias] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(() =>
    Promise.all([api.meuPerfil(), api.minhaFichaAdmissional(), api.minhasFerias()])
      .then(([dadosPerfil, dadosFicha, dadosFerias]) => {
        setPerfil(dadosPerfil)
        setFicha(dadosFicha)
        setFerias(dadosFerias)
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false)), [toast])

  useEffect(() => { load() }, [load])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Minha Conta"
        subtitle="Seus dados cadastrais completos, iguais aos que a administração vê em Colaboradores → Detalhes."
      />
      {perfil && (
        <div className="card minha-conta-card">
          <MinhaContaDetalhes perfil={perfil} ficha={ficha} ferias={ferias} />
        </div>
      )}
    </>
  )
}
