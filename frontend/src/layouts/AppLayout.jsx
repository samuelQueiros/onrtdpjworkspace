import { useEffect, useRef, useState } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'

const Icon = {
  home: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>,
  calendar: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>,
  plus: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" /></svg>,
  grid: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>,
  bell: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" /></svg>,
  file: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>,
  check: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>,
  users: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>,
  building: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2" /><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" /></svg>,
  chart: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /><line x1="2" y1="20" x2="22" y2="20" /></svg>,
  log: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></svg>,
  logout: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" /></svg>,
  chevron: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="6 9 12 15 18 9" /></svg>,
  lock: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>,
  key: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="7.5" cy="15.5" r="5.5"/><path d="M21 2l-9.6 9.6"/><path d="M15.5 7.5l3 3L22 7l-3-3"/></svg>,
}

const PAGES = {
  '/': 'Dashboard',
  '/minhas-ferias': 'Minhas Férias',
  '/solicitar': 'Solicitar Férias',
  '/disponibilidade': 'Disponibilidade',
  '/mural': 'Mural de Avisos',
  '/documentos': 'Documentos',
  '/aprovacoes': 'Aprovação de Férias',
  '/usuarios': 'Usuários',
  '/departamentos': 'Departamentos',
  '/bloqueios': 'Bloqueio de Datas',
  '/relatorios': 'Relatórios',
  '/logs': 'Logs do Sistema',
  '/credenciais': 'Acessos / Senhas',
  '/minhas-credenciais': 'Minhas Credenciais',
}

function LinkItem({ to, end, icon, children, badge }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
      {icon}
      {children}
      {badge > 0 && <span className="nav-badge">{badge}</span>}
    </NavLink>
  )
}

function isBirthdayToday(dataAniversario) {
  if (!dataAniversario) return false
  const today = new Date()
  const [, month, day] = dataAniversario.split('-').map(Number)
  return today.getMonth() + 1 === month && today.getDate() === day
}

export default function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [dropOpen, setDropOpen] = useState(false)
  const [pendentes, setPendentes] = useState(0)
  const [showBirthday, setShowBirthday] = useState(false)
  const dropRef = useRef(null)

  useEffect(() => {
    const handler = event => {
      if (dropRef.current && !dropRef.current.contains(event.target)) setDropOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  useEffect(() => {
    if (user?.role === 'admin') {
      api.feriasPendentes().then(list => setPendentes(list.length)).catch(() => {})
    }
  }, [user, location.pathname])

  useEffect(() => {
    if (!user) return
    const key = `birthday-shown-${user.id}-${new Date().toDateString()}`
    if (isBirthdayToday(user.data_aniversario) && !sessionStorage.getItem(key)) {
      sessionStorage.setItem(key, '1')
      setShowBirthday(true)
    }
  }, [user])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">
            <img src="/logo.png" alt="ONRTDPJ" width="38" height="38" />
          </div>
          <div className="logo-text">
            <strong>ONRTDPJ</strong>
            <span>Gestão RH</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-group">
            <span className="nav-label">Menu</span>
            <LinkItem to="/" end icon={Icon.home}>Dashboard</LinkItem>
            <LinkItem to="/minhas-ferias" icon={Icon.calendar}>Minhas Férias</LinkItem>
            <LinkItem to="/solicitar" icon={Icon.plus}>Solicitar Férias</LinkItem>
            <LinkItem to="/disponibilidade" icon={Icon.grid}>Disponibilidade</LinkItem>
            <LinkItem to="/mural" icon={Icon.bell}>Mural de Avisos</LinkItem>
            <LinkItem to="/documentos" icon={Icon.file}>Documentos</LinkItem>
            <LinkItem to="/minhas-credenciais" icon={Icon.key}>Minhas Credenciais</LinkItem>
          </div>

          {user?.role === 'admin' && (
            <div className="nav-group">
              <span className="nav-label">Administração</span>
              <LinkItem to="/aprovacoes" icon={Icon.check} badge={pendentes}>Aprovações</LinkItem>
              <LinkItem to="/usuarios" icon={Icon.users}>Usuários</LinkItem>
              <LinkItem to="/departamentos" icon={Icon.building}>Departamentos</LinkItem>
              <LinkItem to="/bloqueios" icon={Icon.lock}>Bloqueio de Datas</LinkItem>
              <LinkItem to="/credenciais" icon={Icon.key}>Acessos / Senhas</LinkItem>
              <LinkItem to="/relatorios" icon={Icon.chart}>Relatórios</LinkItem>
              <LinkItem to="/logs" icon={Icon.log}>Logs</LinkItem>
            </div>
          )}
        </nav>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div>
            <div className="topbar-title">{PAGES[location.pathname] ?? 'Gestão RH'}</div>
            <div className="topbar-sub">Sistema de Gestão RH — ONRTDPJ</div>
          </div>

          <div className="topbar-right" ref={dropRef}>
            <button className="user-pill" onClick={() => setDropOpen(open => !open)}>
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
              <div className="dropdown">
                <button className="dropdown-item danger" onClick={handleLogout}>
                  {Icon.logout}
                  Sair do sistema
                </button>
              </div>
            )}
          </div>
        </header>

        <main className="content">{children}</main>
      </div>

      {showBirthday && (
        <div className="bday-overlay" onClick={() => setShowBirthday(false)}>
          <div className="bday-card" onClick={e => e.stopPropagation()}>
            <div className="bday-emoji">🎂</div>
            <h2 className="bday-title">Feliz Aniversário!</h2>
            <p className="bday-msg">
              Parabéns, <strong>{user.nome.split(' ')[0]}</strong>!<br />
              A equipe do ONRTDPJ deseja a você um dia incrível e cheio de alegrias!
            </p>
            <button className="btn btn-primary bday-btn" onClick={() => setShowBirthday(false)}>
              Obrigado! 🎉
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
