import { req } from '../httpClient'

export const envioService = {
  listarEnvios: () => req('GET', '/envios'),
  enviarLembreteFerias: alertaId => req('POST', `/envios/${alertaId}/enviar`),
}
