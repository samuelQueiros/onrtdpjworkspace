import { req } from '../httpClient'

export const alertasService = {
  listarAlertas: () => req('GET', '/alertas'),
  marcarAlertaLido: id => req('PUT', `/alertas/${id}/lido`),
}
