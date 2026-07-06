const FEATURES = [
  'Gestão de Colaboradores',
  'Gestão de Férias',
  'Acessos e Credenciais',
  'Documentos e Atestados',
  'Departamentos',
  'Comunicados Internos',
  'Relatórios Gerenciais',
  'Administração do Sistema',
]

export default function LoginHero() {
  return (
    <section className="login-panel-left">
      <div className="login-brand">
        <div className="login-logo-wrap">
          <div className="login-logo-mark">
            <img src="/logo.png" alt="ONRTDPJ" width="52" height="52" />
          </div>
          <div className="login-logo-text">
            <strong>ONRTDPJ</strong>
            <span>Operador Nacional de RTDPJ</span>
          </div>
        </div>

        <p className="eyebrow">Sistema Interno</p>
        <h1>ONRTDPJ Workspace</h1>
        <p>
          O ambiente unificado para a gestão das operações internas.
        </p>
        <p className="mt-12">
          Uma plataforma desenvolvida para centralizar processos administrativos,
          controlar acessos, organizar documentos e apoiar a gestão de pessoas
          em um único lugar.
        </p>
      </div>

      <div className="login-feature-grid">
        {FEATURES.map(feature => (
          <span key={feature}>{feature}</span>
        ))}
      </div>
    </section>
  )
}
