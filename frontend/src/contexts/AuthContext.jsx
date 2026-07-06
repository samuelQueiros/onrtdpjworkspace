import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'
import { clearToken, getToken, setToken } from '../services/httpClient'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (getToken()) {
      api.me()
        .then(setUser)
        .catch(clearToken)
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, senha) => {
    const data = await api.login(email, senha)
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    clearToken()
    setUser(null)
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
