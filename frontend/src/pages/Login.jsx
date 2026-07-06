import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import LoginForm from '../components/login/LoginForm'
import LoginHero from '../components/login/LoginHero'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'

export default function Login() {
  const { login, user } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  if (user) return <Navigate to="/" replace />

  const submit = async event => {
    event.preventDefault()
    setLoading(true)
    try {
      await login(email, senha)
      navigate('/', { replace: true })
    } catch {
      toast.error('E-mail ou senha inválidos.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrap">
      <LoginHero />
      <LoginForm
        email={email}
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
