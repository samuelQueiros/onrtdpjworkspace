const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export async function parseJson(res) {
  return res.json().catch(() => ({}))
}

function errorMessage(detail, fallback) {
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const messages = detail.map(item => {
      if (typeof item === 'string') return item
      const field = Array.isArray(item?.loc) ? item.loc.filter(part => !['body', 'query', 'path'].includes(part)).join('.') : ''
      return `${field ? `${field}: ` : ''}${item?.msg || 'valor inválido'}`
    }).filter(Boolean)
    if (messages.length) return messages.join(' · ')
  }
  if (detail && typeof detail === 'object' && typeof detail.message === 'string') return detail.message
  return fallback
}

function requestError(res, data, fallback) {
  const error = new Error(errorMessage(data.detail, fallback))
  error.status = res.status
  return error
}

function handleUnauthorized(res) {
  if (res.status === 401) {
    window.dispatchEvent(new Event('auth:unauthorized'))
  }
}

export async function req(method, path, body = null) {
  const headers = {
    ...(body ? { 'Content-Type': 'application/json' } : {}),
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    credentials: 'include',
    body: body ? JSON.stringify(body) : null,
  })

  const data = await parseJson(res)
  if (!res.ok) {
    handleUnauthorized(res)
    throw requestError(res, data, 'Erro na requisição')
  }
  return data
}

export async function upload(path, formData) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  })

  const data = await parseJson(res)
  if (!res.ok) {
    handleUnauthorized(res)
    throw requestError(res, data, 'Erro no upload')
  }
  return data
}

export async function download(path) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'GET',
    credentials: 'include',
  })

  if (!res.ok) {
    const data = await parseJson(res)
    handleUnauthorized(res)
    throw requestError(res, data, 'Erro ao baixar arquivo')
  }

  return res.blob()
}

export async function postForm(path, form) {
  const res = await fetch(`${BASE}${path}`, { method: 'POST', body: form, credentials: 'include' })
  const data = await parseJson(res)
  if (!res.ok) throw requestError(res, data, 'Credenciais inválidas')
  return data
}
