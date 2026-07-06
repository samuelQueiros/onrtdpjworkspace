import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import BirthdayModal from '../components/estrutura/BirthdayModal'
import Sidebar from '../components/estrutura/Sidebar'
import Topbar from '../components/estrutura/Topbar'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'

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
      <Sidebar user={user} pendingApprovals={pendentes} />

      <div className="main-area">
        <Topbar
          user={user}
          pathname={location.pathname}
          dropOpen={dropOpen}
          dropRef={dropRef}
          onToggleDrop={() => setDropOpen(open => !open)}
          onLogout={handleLogout}
        />

        <main className="content">{children}</main>
      </div>

      {showBirthday && <BirthdayModal user={user} onClose={() => setShowBirthday(false)} />}
    </div>
  )
}
