import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null)).finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const unauthorized = () => setUser(null)
    window.addEventListener('auth:unauthorized', unauthorized)
    return () => window.removeEventListener('auth:unauthorized', unauthorized)
  }, [])

  const login = async (email, senha) => {
    const data = await api.login(email, senha)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    setUser(null)
    api.logout().catch(() => {})
  }

  const refreshUser = () =>
    api.me().then(u => { setUser(u); return u })

  return (
    <Ctx.Provider value={{ user, login, logout, loading, refreshUser }}>
      {children}
    </Ctx.Provider>
  )
}

export const useAuth = () => useContext(Ctx)
