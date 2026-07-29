import { req } from '../httpClient'

export const feriasService = {
  minhasFerias: () => req('GET', '/ferias/me'),
  disponibilidade: () => req('GET', '/ferias/disponibilidade'),
  feriados: year => req('GET', `/ferias/feriados/${year}`),
  registrarFerias: body => req('POST', '/ferias', body),
  editarFerias: (id, body) => req('PUT', `/ferias/${id}`, body),
  cancelarFerias: id => req('DELETE', `/ferias/${id}`),
  todasFerias: () => req('GET', '/ferias/todas'),
  aprovarFerias: id => req('PUT', `/ferias/${id}/aprovar`),
  rejeitarFerias: (id, motivo) => req('PUT', `/ferias/${id}/rejeitar`, { motivo_rejeicao: motivo }),
}
