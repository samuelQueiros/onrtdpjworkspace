const Icon = {
  chevron: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="6 9 12 15 18 9" /></svg>,
  logout: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>,
}

const PAGES = {
  '/': 'Dashboard',
  '/minhas-ferias': 'Minhas Férias',
  '/minhas-autorizacoes': 'Minhas Autorizações',
  '/solicitar': 'Solicitações',
  '/disponibilidade': 'Disponibilidade',
  '/mural': 'Mural de Avisos',
  '/documentos': 'Documentos',
  '/aprovacoes': 'Aprovações',
  '/usuarios': 'Usuários',
  '/patrimonios': 'Patrimônios',
  '/bloqueios': 'Bloqueio de Datas',
  '/relatorios': 'Relatórios',
  '/logs': 'Logs do Sistema',
  '/credenciais': 'Acessos / Senhas',
  '/minhas-credenciais': 'Minhas Credenciais',
  '/configuracoes': 'Configurações',
}

export default function Topbar({ user, pathname, dropOpen, dropRef, onToggleDrop, onLogout }) {
  return (
    <header className="topbar">
      <div>
        <div className="topbar-title">{PAGES[pathname] ?? 'Gestão RH'}</div>
        <div className="topbar-sub">Sistema de Gestão RH - ONRTDPJ</div>
      </div>

      <div className="topbar-right" ref={dropRef}>
        <button
          className="user-pill"
          type="button"
          aria-expanded={dropOpen}
          aria-controls="user-account-menu"
          aria-haspopup="menu"
          onClick={onToggleDrop}
        >
          <div
            className="avatar"
            style={{ background: user?.cor || 'var(--navy)' }}
          >
            {user?.nome?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <div className="user-pill-name">{user?.nome}</div>
            <div className="user-pill-role">{user?.role === 'admin' ? 'Administrador' : 'Colaborador'}</div>
          </div>
          <span className="chevron">{Icon.chevron}</span>
        </button>

        {dropOpen && (
          <div id="user-account-menu" className="dropdown" role="menu">
            <button className="dropdown-item danger" type="button" role="menuitem" onClick={onLogout}>
              {Icon.logout}
              Sair do sistema
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
