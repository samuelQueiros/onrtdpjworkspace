const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const getToken = () => localStorage.getItem('token')
export const setToken = token => localStorage.setItem('token', token)
export const clearToken = () => localStorage.removeItem('token')

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function parseJson(res) {
  return res.json().catch(() => ({}))
}

function handleUnauthorized(res) {
  if (res.status === 401) {
    clearToken()
  }
}

export async function req(method, path, body = null) {
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
    throw new Error(data.detail || 'Erro na requisição')
  }
  return data
}

export async function upload(path, formData) {
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

export async function download(path) {
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

export async function postForm(path, form) {
  const res = await fetch(`${BASE}${path}`, { method: 'POST', body: form })
  const data = await parseJson(res)
  if (!res.ok) throw new Error(data.detail || 'Credenciais inválidas')
  return data
}
