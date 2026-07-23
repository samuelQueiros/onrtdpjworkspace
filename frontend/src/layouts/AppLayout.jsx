import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import BirthdayModal from '../components/estrutura/BirthdayModal'
import NotificacaoFeriasModal from '../components/estrutura/NotificacaoFeriasModal'
import Sidebar from '../components/estrutura/Sidebar'
import Topbar from '../components/estrutura/Topbar'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'

function isBirthdayToday(dataAniversario) {
  if (!dataAniversario) return false
  const today = new Date()
  const [, month, day] = dataAniversario.split('-').map(Number)
  return today.getMonth() + 1 === month && today.getDate() === day
}

function avisoFeriasDismissKey(alertaId) {
  return `ferias-4dias-dismissed-${alertaId}-${new Date().toDateString()}`
}

const PENDENTES_POLL_MS = 60000

export default function AppLayout({ children }) {
  const { user, logout } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const location = useLocation()
  const [dropOpen, setDropOpen] = useState(false)
  const [pendentes, setPendentes] = useState(0)
  const [showBirthday, setShowBirthday] = useState(false)
  const [avisosFerias, setAvisosFerias] = useState([])
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
      const carregarPendentes = () => api.pendenciasAprovacoes()
        .then(data => setPendentes(data.total))
        .catch(error => console.error('Falha ao carregar aprovações pendentes', error))
      carregarPendentes()
      window.addEventListener('approvals:changed', carregarPendentes)
      const intervalId = window.setInterval(carregarPendentes, PENDENTES_POLL_MS)
      return () => {
        window.removeEventListener('approvals:changed', carregarPendentes)
        window.clearInterval(intervalId)
      }
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

  useEffect(() => {
    if (user?.role !== 'admin') {
      setAvisosFerias([])
      return
    }
    const carregarAvisosFerias = () => api.listarAlertas()
      .then(lista => setAvisosFerias(lista.filter(alerta => {
        if (alerta.tipo === 'ferias_5dias') return !alerta.lido
        if (alerta.tipo === 'ferias_4dias') return !sessionStorage.getItem(avisoFeriasDismissKey(alerta.id))
        return false
      })))
      .catch(error => console.error('Falha ao carregar avisos de ferias', error))
    carregarAvisosFerias()
    const intervalId = window.setInterval(carregarAvisosFerias, PENDENTES_POLL_MS)
    return () => window.clearInterval(intervalId)
  }, [user, location.pathname])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const fecharAvisoFerias = async alerta => {
    setAvisosFerias(prev => prev.filter(item => item.id !== alerta.id))

    if (alerta.tipo === 'ferias_4dias') {
      sessionStorage.setItem(avisoFeriasDismissKey(alerta.id), '1')
      return
    }

    try {
      await api.marcarAlertaLido(alerta.id)
    } catch (error) {
      console.error('Falha ao marcar aviso de ferias como lido', error)
    }
  }

  const copiarModeloFerias = sucesso => {
    if (sucesso) toast.success('Modelo de e-mail copiado para a área de transferência.')
    else toast.error('Não foi possível copiar o modelo automaticamente.')
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

      {!showBirthday && avisosFerias.length > 0 && (
        <NotificacaoFeriasModal
          alerta={avisosFerias[0]}
          total={avisosFerias.length}
          onFechar={() => fecharAvisoFerias(avisosFerias[0])}
          onCopiar={copiarModeloFerias}
        />
      )}
    </div>
  )
}
