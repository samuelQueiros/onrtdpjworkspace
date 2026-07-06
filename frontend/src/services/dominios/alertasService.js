import { req } from '../httpClient'

export const alertasService = {
  listarAlertas: () => req('GET', '/alertas'),
  marcarAlertaLido: id => req('PUT', `/alertas/${id}/lido`),
  marcarTodosAlertasLidos: () => req('PUT', '/alertas/marcar-todos-lidos'),
}
