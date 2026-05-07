import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
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
          <h1>Gestão de férias com clareza e controle.</h1>
          <p>Solicitações, disponibilidade, saldos e relatórios em uma interface simples para equipes administrativas.</p>
        </div>
        <div className="login-feature-grid">
          <span>Calendário de disponibilidade</span>
          <span>Controle de saldo</span>
          <span>Aprovação de férias</span>
          <span>Mural de avisos</span>
          <span>Documentos e atestados</span>
          <span>Relatórios administrativos</span>
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
            <label>E-mail</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Senha</label>
            <input
              type="password"
              value={senha}
              onChange={e => setSenha(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button className="btn btn-primary btn-lg" type="submit" disabled={loading}>
            {loading && <span className="inline-spinner" />}
            Entrar no sistema
          </button>

          <p className="login-hint muted">Acesso inicial: admin@sistema.com / admin123</p>
        </form>
      </section>
    </div>
  )
}
