import { req } from '../httpClient'

export const avisosService = {
  listarAvisos: () => req('GET', '/avisos'),
  listarTodosAvisos: () => req('GET', '/avisos/todos'),
  criarAviso: body => req('POST', '/avisos', body),
  editarAviso: (id, body) => req('PUT', `/avisos/${id}`, body),
  excluirAviso: id => req('DELETE', `/avisos/${id}`),
}
