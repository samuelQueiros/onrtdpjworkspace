const AVISO_FERIAS_DISPENSADO_PREFIX = 'ferias-4dias-dismissed-'

export function avisoFeriasDismissKey(alertaId) {
  return `${AVISO_FERIAS_DISPENSADO_PREFIX}${alertaId}`
}

export function limparAvisosFeriasDispensados() {
  if (typeof sessionStorage === 'undefined') return

  Object.keys(sessionStorage)
    .filter(key => key.startsWith(AVISO_FERIAS_DISPENSADO_PREFIX))
    .forEach(key => sessionStorage.removeItem(key))
}
