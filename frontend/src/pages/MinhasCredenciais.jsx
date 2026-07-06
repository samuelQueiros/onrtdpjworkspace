import { useEffect, useState } from 'react'
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
      // Falha silenciosa se clipboard não disponível
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
          {credenciais.map(c => (
            <div className="card" key={c.id}>
              <div className="card-header">
                <h2 className="card-title">{c.descricao}</h2>
              </div>
              <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ minWidth: 60, color: 'var(--muted)', fontSize: 13 }}>E-mail</span>
                  <span style={{ flex: 1 }}>{c.email}</span>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => copiar(`email-${c.id}`, c.email)}
                  >
                    {copiado[`email-${c.id}`] ? 'Copiado!' : 'Copiar'}
                  </button>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ minWidth: 60, color: 'var(--muted)', fontSize: 13 }}>Senha</span>
                  <span style={{ flex: 1, fontFamily: 'monospace', letterSpacing: visiveis[c.id] ? 0 : 2 }}>
                    {visiveis[c.id] ? c.senha : '••••••••'}
                  </span>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => toggleVisivel(c.id)}
                  >
                    {visiveis[c.id] ? 'Ocultar' : 'Mostrar'}
                  </button>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => copiar(`senha-${c.id}`, c.senha)}
                  >
                    {copiado[`senha-${c.id}`] ? 'Copiado!' : 'Copiar'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
