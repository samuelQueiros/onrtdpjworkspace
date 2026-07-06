import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import LoginForm from '../components/login/LoginForm'
import LoginHero from '../components/login/LoginHero'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  if (user) return <Navigate to="/" replace />

  const submit = async event => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, senha)
      navigate('/', { replace: true })
    } catch {
      setError('E-mail ou senha inválidos.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrap">
      <LoginHero />
      <LoginForm
        email={email}
        error={error}
        loading={loading}
        onEmailChange={setEmail}
        onSenhaChange={setSenha}
        onSubmit={submit}
        onTogglePassword={() => setShowPass(value => !value)}
        senha={senha}
        showPass={showPass}
      />
    </div>
  )
}
