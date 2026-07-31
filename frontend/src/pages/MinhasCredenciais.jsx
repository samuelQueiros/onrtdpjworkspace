import { useEffect, useState } from 'react'
import '../styles/pages/minhas-credenciais.css'
import CredencialCompartilhadaCard from '../components/minhasCredenciais/CredencialCompartilhadaCard'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { EmptyState, LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function MinhasCredenciais() {
  const toast = useToast()
  const [credenciais, setCredenciais] = useState([])
  const [loading, setLoading] = useState(true)
  const [segredos, setSegredos] = useState({})
  const [revelando, setRevelando] = useState({})
  const [copiado, setCopiado] = useState({})

  useEffect(() => {
    api.minhasCredenciais()
      .then(setCredenciais)
      .catch(err => toast.error(err.message))
      .finally(() => setLoading(false))
  }, [toast])

  const revelar = async (id, senhaAtual) => {
    setRevelando(prev => ({ ...prev, [id]: true }))
    try {
      const response = await api.revelarCredencial(id, senhaAtual)
      setSegredos(prev => ({ ...prev, [id]: response.senha }))
      return true
    } catch (err) {
      toast.error(err.message)
      return false
    } finally {
      setRevelando(prev => ({ ...prev, [id]: false }))
    }
  }

  const ocultar = id => {
    setSegredos(prev => {
      const atualizados = { ...prev }
      delete atualizados[id]
      return atualizados
    })
  }

  const copiar = async (id, texto) => {
    try {
      await navigator.clipboard.writeText(texto)
      setCopiado(prev => ({ ...prev, [id]: true }))
      setTimeout(() => setCopiado(prev => ({ ...prev, [id]: false })), 1500)
    } catch {
      // Falha silenciosa se clipboard não disponível.
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Minhas Credenciais"
        subtitle="Acessos e senhas compartilhados com você pela administração."
      />

      {credenciais.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Nenhuma credencial disponível"
            text="Você ainda não tem acesso a nenhuma credencial. Solicite ao administrador."
          />
        </div>
      ) : (
        <div className="stack-16">
          {credenciais.map(credencial => (
            <CredencialCompartilhadaCard
              key={credencial.id}
              copiado={copiado}
              credencial={credencial}
              onCopiar={copiar}
              onOcultar={ocultar}
              onRevelar={revelar}
              revelando={!!revelando[credencial.id]}
              segredo={segredos[credencial.id]}
            />
          ))}
        </div>
      )}
    </>
  )
}
