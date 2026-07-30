const PREFIX = 'avisos-vistos-'

function chave(userId) {
  return `${PREFIX}${userId}`
}

export function obterAvisosVistos(userId) {
  try {
    const raw = localStorage.getItem(chave(userId))
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch {
    return new Set()
  }
}

export function marcarAvisosComoVistos(userId, avisoIds) {
  if (!userId || !avisoIds?.length) return
  const vistos = obterAvisosVistos(userId)
  const antes = vistos.size
  avisoIds.forEach(id => vistos.add(id))
  if (vistos.size === antes) return
  localStorage.setItem(chave(userId), JSON.stringify([...vistos]))
  window.dispatchEvent(new Event('avisos:changed'))
}

export function contarAvisosNaoVistos(userId, avisos) {
  const vistos = obterAvisosVistos(userId)
  return avisos.filter(aviso => !vistos.has(aviso.id)).length
}
