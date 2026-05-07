import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import PrivateRoute from './components/PrivateRoute'
import { AuthProvider } from './context/AuthContext'
import Aprovacoes from './pages/Aprovacoes'
import Dashboard from './pages/Dashboard'
import Departamentos from './pages/Departamentos'
import Disponibilidade from './pages/Disponibilidade'
import Documentos from './pages/Documentos'
import Login from './pages/Login'
import Logs from './pages/Logs'
import MinhasFerias from './pages/MinhasFerias'
import Mural from './pages/Mural'
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
          <Route path="/mural" element={<Shell><Mural /></Shell>} />
          <Route path="/documentos" element={<Shell><Documentos /></Shell>} />
          <Route path="/aprovacoes" element={<Shell adminOnly><Aprovacoes /></Shell>} />
          <Route path="/usuarios" element={<Shell adminOnly><Usuarios /></Shell>} />
          <Route path="/departamentos" element={<Shell adminOnly><Departamentos /></Shell>} />
          <Route path="/relatorios" element={<Shell adminOnly><Relatorios /></Shell>} />
          <Route path="/logs" element={<Shell adminOnly><Logs /></Shell>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
