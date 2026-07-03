const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

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
  if (!res.ok) throw new Error(data.detail || 'Erro na requisição')
  return data
}

async function upload(path, formData) {
  const headers = {}
  if (token()) headers.Authorization = `Bearer ${token()}`

  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers,
    body: formData,
  })

  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || 'Erro no upload')
  return data
}

export const api = {
  // Auth
  login(email, senha) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', senha)
    return fetch(`${BASE}/auth/login`, { method: 'POST', body: form }).then(async res => {
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(data.detail || 'Credenciais inválidas')
      return data
    })
  },
  me: () => req('GET', '/auth/me'),
  updateConfig: body => req('PUT', '/me/configuracoes', body),

  // Férias
  minhasFerias: () => req('GET', '/ferias/me'),
  disponibilidade: () => req('GET', '/ferias/disponibilidade'),
  feriados: year => req('GET', `/ferias/feriados/${year}`),
  registrarFerias: body => req('POST', '/ferias', body),
  editarFerias: (id, body) => req('PUT', `/ferias/${id}`, body),
  cancelarFerias: id => req('DELETE', `/ferias/${id}`),
  // Aprovação (admin)
  feriasPendentes: () => req('GET', '/ferias/pendentes'),
  todasFerias: () => req('GET', '/ferias/todas'),
  aprovarFerias: id => req('PUT', `/ferias/${id}/aprovar`),
  rejeitarFerias: (id, motivo) => req('PUT', `/ferias/${id}/rejeitar`, { motivo_rejeicao: motivo }),

  // Usuários
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
  downloadDocumentoUrl: id => `${BASE}/documentos/${id}/download?token=${token()}`,
  visualizarDocumentoUrl: id => `${BASE}/documentos/${id}/visualizar`,
  excluirDocumento: id => req('DELETE', `/documentos/${id}`),

  // Relatórios e Logs
  relatorios: () => req('GET', '/relatorios'),
  dashboard: () => req('GET', '/dashboard'),
  logs: () => req('GET', '/logs'),

  // Importação Excel
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
