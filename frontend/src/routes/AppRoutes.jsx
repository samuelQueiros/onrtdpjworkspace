import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import PrivateRoute from '../components/PrivateRoute'
import AppLayout from '../layouts/AppLayout'
const Aprovacoes = lazy(() => import('../pages/Aprovacoes'))
const Bloqueios = lazy(() => import('../pages/Bloqueios'))
const Credenciais = lazy(() => import('../pages/Credenciais'))
const MinhasCredenciais = lazy(() => import('../pages/MinhasCredenciais'))
const Dashboard = lazy(() => import('../pages/Dashboard'))
const Disponibilidade = lazy(() => import('../pages/Disponibilidade'))
const Documentos = lazy(() => import('../pages/Documentos'))
const Login = lazy(() => import('../pages/Login'))
const Logs = lazy(() => import('../pages/Logs'))
const MinhasFerias = lazy(() => import('../pages/MinhasFerias'))
const Mural = lazy(() => import('../pages/Mural'))
const Relatorios = lazy(() => import('../pages/Relatorios'))
const SolicitarFerias = lazy(() => import('../pages/SolicitarFerias'))
const Usuarios = lazy(() => import('../pages/Usuarios'))
const Configuracoes = lazy(() => import('../pages/Configuracoes'))
const Patrimonios = lazy(() => import('../pages/Patrimonios'))
const MinhasAutorizacoes = lazy(() => import('../pages/MinhasAutorizacoes'))

function Shell({ children, adminOnly = false }) {
  return (
    <PrivateRoute adminOnly={adminOnly}>
      <AppLayout>{children}</AppLayout>
    </PrivateRoute>
  )
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<div className="loading-screen"><div className="spinner" /><span>Carregando...</span></div>}>
      <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Shell><Dashboard /></Shell>} />
      <Route path="/minhas-ferias" element={<Shell><MinhasFerias /></Shell>} />
      <Route path="/minhas-autorizacoes" element={<Shell><MinhasAutorizacoes /></Shell>} />
      <Route path="/solicitar" element={<Shell><SolicitarFerias /></Shell>} />
      <Route path="/disponibilidade" element={<Shell><Disponibilidade /></Shell>} />
      <Route path="/mural" element={<Shell><Mural /></Shell>} />
      <Route path="/documentos" element={<Shell><Documentos /></Shell>} />
      <Route path="/aprovacoes" element={<Shell adminOnly><Aprovacoes /></Shell>} />
      <Route path="/usuarios" element={<Shell adminOnly><Usuarios /></Shell>} />
      <Route path="/patrimonios" element={<Shell adminOnly><Patrimonios /></Shell>} />
      <Route path="/bloqueios" element={<Shell adminOnly><Bloqueios /></Shell>} />
      <Route path="/relatorios" element={<Shell adminOnly><Relatorios /></Shell>} />
      <Route path="/logs" element={<Shell adminOnly><Logs /></Shell>} />
      <Route path="/credenciais" element={<Shell adminOnly><Credenciais /></Shell>} />
      <Route path="/configuracoes" element={<Shell adminOnly><Configuracoes /></Shell>} />
      <Route path="/minhas-credenciais" element={<Shell><MinhasCredenciais /></Shell>} />
      <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
