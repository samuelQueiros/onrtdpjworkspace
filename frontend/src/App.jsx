import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import PrivateRoute from './components/PrivateRoute'
import { AuthProvider } from './context/AuthContext'
import Dashboard from './pages/Dashboard'
import Disponibilidade from './pages/Disponibilidade'
import Login from './pages/Login'
import Logs from './pages/Logs'
import MinhasFerias from './pages/MinhasFerias'
import Relatorios from './pages/Relatorios'
import SolicitarFerias from './pages/SolicitarFerias'
import Usuarios from './pages/Usuarios'

function Shell({ children, adminOnly = false }) {
  return (
    <PrivateRoute adminOnly={adminOnly}>
      <Layout>{children}</Layout>
    </PrivateRoute>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Shell><Dashboard /></Shell>} />
          <Route path="/minhas-ferias" element={<Shell><MinhasFerias /></Shell>} />
          <Route path="/solicitar" element={<Shell><SolicitarFerias /></Shell>} />
          <Route path="/disponibilidade" element={<Shell><Disponibilidade /></Shell>} />
          <Route path="/usuarios" element={<Shell adminOnly><Usuarios /></Shell>} />
          <Route path="/relatorios" element={<Shell adminOnly><Relatorios /></Shell>} />
          <Route path="/logs" element={<Shell adminOnly><Logs /></Shell>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
