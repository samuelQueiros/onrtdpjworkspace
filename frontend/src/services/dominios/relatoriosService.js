import { req } from '../httpClient'

export const relatoriosService = {
  relatorios: () => req('GET', '/relatorios'),
  dashboard: () => req('GET', '/dashboard'),
  logs: () => req('GET', '/logs'),
}
