const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const getToken = () => localStorage.getItem('token')

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseJson(res) {
  return res.json().catch(() => ({}))
}

function handleUnauthorized(res) {
  if (res.status === 401) {
    localStorage.removeItem('token')
  }
}

async function req(method, path, body = null) {
  const headers = {
    ...authHeaders(),
    ...(body ? { 'Content-Type': 'application/json' } : {}),
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  })

  const data = await parseJson(res)
  if (!res.ok) {
    handleUnauthorized(res)
    throw new Error(data.detail || 'Erro na requisicao')
  }
  return data
}

async function upload(path, formData) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: authHeaders(),
    body: formData,
  })

  const data = await parseJson(res)
  if (!res.ok) {
    handleUnauthorized(res)
    throw new Error(data.detail || 'Erro no upload')
  }
  return data
}

async function download(path) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'GET',
    headers: authHeaders(),
  })

  if (!res.ok) {
    const data = await parseJson(res)
    handleUnauthorized(res)
    throw new Error(data.detail || 'Erro ao baixar arquivo')
  }

  return res.blob()
}

export const api = {
  // Auth
  login(email, senha) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', senha)
    return fetch(`${BASE}/auth/login`, { method: 'POST', body: form }).then(async res => {
      const data = await parseJson(res)
      if (!res.ok) throw new Error(data.detail || 'Credenciais invalidas')
      return data
    })
  },
  me: () => req('GET', '/auth/me'),
  updateConfig: body => req('PUT', '/me/configuracoes', body),

  // Ferias
  minhasFerias: () => req('GET', '/ferias/me'),
  disponibilidade: () => req('GET', '/ferias/disponibilidade'),
  feriados: year => req('GET', `/ferias/feriados/${year}`),
  registrarFerias: body => req('POST', '/ferias', body),
  editarFerias: (id, body) => req('PUT', `/ferias/${id}`, body),
  cancelarFerias: id => req('DELETE', `/ferias/${id}`),
  feriasPendentes: () => req('GET', '/ferias/pendentes'),
  todasFerias: () => req('GET', '/ferias/todas'),
  aprovarFerias: id => req('PUT', `/ferias/${id}/aprovar`),
  rejeitarFerias: (id, motivo) => req('PUT', `/ferias/${id}/rejeitar`, { motivo_rejeicao: motivo }),

  // Usuarios
  listarUsuarios: () => req('GET', '/users'),
  listarAniversariantes: () => req('GET', '/users/aniversariantes'),
  criarUsuario: body => req('POST', '/users', body),
  editarUsuario: (id, body) => req('PUT', `/users/${id}`, body),
  excluirUsuario: id => req('DELETE', `/users/${id}`),

  // Departamentos
  listarDepartamentos: () => req('GET', '/departamentos'),
  criarDepartamento: body => req('POST', '/departamentos', body),
  editarDepartamento: (id, body) => req('PUT', `/departamentos/${id}`, body),
  excluirDepartamento: id => req('DELETE', `/departamentos/${id}`),

  // Avisos / Mural
  listarAvisos: () => req('GET', '/avisos'),
  listarTodosAvisos: () => req('GET', '/avisos/todos'),
  criarAviso: body => req('POST', '/avisos', body),
  editarAviso: (id, body) => req('PUT', `/avisos/${id}`, body),
  excluirAviso: id => req('DELETE', `/avisos/${id}`),

  // Documentos
  meusDocumentos: () => req('GET', '/documentos/me'),
  documentosUsuario: userId => req('GET', `/documentos/usuario/${userId}`),
  uploadDocumento: formData => upload('/documentos/upload', formData),
  downloadDocumento: id => download(`/documentos/${id}/download`),
  excluirDocumento: id => req('DELETE', `/documentos/${id}`),

  // Relatorios e Logs
  relatorios: () => req('GET', '/relatorios'),
  dashboard: () => req('GET', '/dashboard'),
  logs: () => req('GET', '/logs'),

  // Importacao Excel
  importarFerias: formData => upload('/importacao/ferias', formData),
  importarLogs: formData => upload('/importacao/logs', formData),

  // Bloqueios de datas
  listarBloqueios: () => req('GET', '/bloqueios'),
  criarBloqueio: body => req('POST', '/bloqueios', body),
  editarBloqueio: (id, body) => req('PUT', `/bloqueios/${id}`, body),
  excluirBloqueio: id => req('DELETE', `/bloqueios/${id}`),

  // Alertas
  listarAlertas: () => req('GET', '/alertas'),
  marcarAlertaLido: id => req('PUT', `/alertas/${id}/lido`),
  marcarTodosAlertasLidos: () => req('PUT', '/alertas/marcar-todos-lidos'),

  // Credenciais (admin)
  listarCredenciais: () => req('GET', '/credenciais'),
  criarCredencial: body => req('POST', '/credenciais', body),
  editarCredencial: (id, body) => req('PUT', `/credenciais/${id}`, body),
  excluirCredencial: id => req('DELETE', `/credenciais/${id}`),
  usuariosCredencial: id => req('GET', `/credenciais/${id}/usuarios`),
  salvarPermissoes: (id, user_ids) => req('PUT', `/credenciais/${id}/permissoes`, { user_ids }),

  // Credenciais (colaborador)
  minhasCredenciais: () => req('GET', '/credenciais/minhas'),
}
