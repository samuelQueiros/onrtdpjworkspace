import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@sistema.com')
  const [senha, setSenha] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to="/" replace />

  const submit = async event => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, senha)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrap">
      <section className="login-panel-left">
        <div className="login-brand">
          <div className="login-logo">F</div>
          <p className="eyebrow">ONRTDPJ</p>
          <h1>Gestao de ferias com clareza e controle.</h1>
          <p>Solicitacoes, disponibilidade, saldos e relatorios em uma interface simples para equipes administrativas.</p>
        </div>
        <div className="login-feature-grid">
          <span>Calendario de disponibilidade</span>
          <span>Controle de saldo</span>
          <span>Relatorios administrativos</span>
        </div>
      </section>

      <section className="login-panel-right">
        <form className="login-card" onSubmit={submit}>
          <div>
            <p className="eyebrow">Bem-vindo</p>
            <h2>Acesse sua conta</h2>
            <p className="login-muted">Use suas credenciais do sistema para continuar.</p>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={event => setEmail(event.target.value)} required />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input type="password" value={senha} onChange={event => setSenha(event.target.value)} required />
          </div>

          <button className="btn btn-primary btn-lg" type="submit" disabled={loading}>
            {loading && <span className="inline-spinner" />}
            Entrar
          </button>

          <p className="login-hint">Acesso inicial: admin@sistema.com / admin123</p>
        </form>
      </section>
    </div>
  )
}
