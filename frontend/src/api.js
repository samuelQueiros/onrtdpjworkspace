const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const token = () => localStorage.getItem('token')

async function req(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' }
  if (token()) headers.Authorization = `Bearer ${token()}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  })

  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || 'Erro na requisicao')
  return data
}

export const api = {
  login(email, senha) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', senha)

    return fetch(`${BASE}/auth/login`, { method: 'POST', body: form }).then(async res => {
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Credenciais invalidas')
      return data
    })
  },

  me: () => req('GET', '/auth/me'),
  updateConfig: body => req('PUT', '/me/configuracoes', body),

  minhasFerias: () => req('GET', '/ferias/me'),
  disponibilidade: () => req('GET', '/ferias/disponibilidade'),
  registrarFerias: body => req('POST', '/ferias', body),
  editarFerias: (id, body) => req('PUT', `/ferias/${id}`, body),
  cancelarFerias: id => req('DELETE', `/ferias/${id}`),

  listarUsuarios: () => req('GET', '/users'),
  criarUsuario: body => req('POST', '/users', body),
  editarUsuario: (id, body) => req('PUT', `/users/${id}`, body),

  relatorios: () => req('GET', '/relatorios'),
  logs: () => req('GET', '/logs'),
}
