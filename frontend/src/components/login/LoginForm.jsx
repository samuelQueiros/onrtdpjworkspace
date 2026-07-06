function PasswordIcon({ visible }) {
  return visible ? (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
  ) : (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
  )
}

export default function LoginForm({
  email,
  error,
  loading,
  onEmailChange,
  onSenhaChange,
  onSubmit,
  onTogglePassword,
  senha,
  showPass,
}) {
  return (
    <section className="login-panel-right">
      <form className="login-card" onSubmit={onSubmit}>
        <div className="login-right-logo">
          <div className="login-right-logo-mark">
            <img src="/logo.png" alt="ONRTDPJ" width="42" height="42" />
          </div>
          <div className="login-right-logo-text">
            <strong>ONRTDPJ</strong>
            <span>Gestão RH</span>
          </div>
        </div>

        <div>
          <p className="eyebrow">Bem-vindo</p>
          <h2>Acesse sua conta</h2>
          <p className="login-muted mt-4">
            Use suas credenciais do sistema para continuar.
          </p>
        </div>

        {error && (
          <div className="alert alert-error" role="alert">
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="email">E-mail</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={event => onEmailChange(event.target.value)}
            placeholder="seu@email.com"
            autoComplete="username"
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="senha">Senha</label>
          <div className="relative-field">
            <input
              id="senha"
              type={showPass ? 'text' : 'password'}
              value={senha}
              onChange={event => onSenhaChange(event.target.value)}
              placeholder="********"
              autoComplete="current-password"
              className="login-password-input"
              disabled={loading}
              required
            />
            <button
              type="button"
              onClick={onTogglePassword}
              className="login-password-toggle"
              aria-label={showPass ? 'Ocultar senha' : 'Mostrar senha'}
              aria-pressed={showPass}
              title={showPass ? 'Ocultar senha' : 'Mostrar senha'}
              disabled={loading}
            >
              <PasswordIcon visible={showPass} />
            </button>
          </div>
        </div>

        <button
          className="btn btn-primary btn-lg login-submit"
          type="submit"
          disabled={loading}
        >
          {loading && <span className="inline-spinner" />}
          {loading ? 'Entrando...' : 'Entrar no sistema'}
        </button>

        <p className="login-hint muted">
          Acesso inicial: <strong>admin@sistema.com</strong> / admin123
        </p>
      </form>
    </section>
  )
}
