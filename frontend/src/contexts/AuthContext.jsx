import { createContext, useCallback, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [availabilityError, setAvailabilityError] = useState(null)

  const loadSession = useCallback(() => {
    setLoading(true)
    setAvailabilityError(null)
    return api.me()
      .then(setUser)
      .catch(error => {
        setUser(null)
        if (error.status !== 401) setAvailabilityError(error.message || 'Não foi possível acessar o servidor.')
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    loadSession()
  }, [loadSession])

  useEffect(() => {
    const unauthorized = () => setUser(null)
    window.addEventListener('auth:unauthorized', unauthorized)
    return () => window.removeEventListener('auth:unauthorized', unauthorized)
  }, [])

  const login = async (email, senha) => {
    const data = await api.login(email, senha)
    setAvailabilityError(null)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    setUser(null)
    api.logout().catch(error => console.error('Falha ao encerrar sessão no servidor', error))
  }

  const refreshUser = () =>
    api.me().then(u => { setUser(u); return u })

  return (
    <Ctx.Provider value={{ user, login, logout, loading, availabilityError, retrySession: loadSession, refreshUser }}>
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)
