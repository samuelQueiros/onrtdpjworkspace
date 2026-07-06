import { useEffect, useState } from 'react'
import CredencialCompartilhadaCard from '../components/minhasCredenciais/CredencialCompartilhadaCard'
import { api } from '../services/api'
import { EmptyState, LoadingCard, PageHeader } from './_helpers'

export default function MinhasCredenciais() {
  const [credenciais, setCredenciais] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [visiveis, setVisiveis] = useState({})
  const [copiado, setCopiado] = useState({})

  useEffect(() => {
    api.minhasCredenciais()
      .then(setCredenciais)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const toggleVisivel = id => {
    setVisiveis(prev => ({ ...prev, [id]: !prev[id] }))
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

      {error && <div className="alert alert-error">{error}</div>}

      {credenciais.length === 0 ? (
        <div className="card">
          <EmptyState
            title="Nenhuma credencial disponível"
            text="Você ainda não tem acesso a nenhuma credencial. Solicite ao administrador."
          />
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {credenciais.map(credencial => (
            <CredencialCompartilhadaCard
              key={credencial.id}
              copiado={copiado}
              credencial={credencial}
              onCopiar={copiar}
              onToggleVisivel={toggleVisivel}
              visivel={!!visiveis[credencial.id]}
            />
          ))}
        </div>
      )}
    </>
  )
}
