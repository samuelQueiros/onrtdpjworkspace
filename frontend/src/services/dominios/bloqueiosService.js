import { req } from '../httpClient'

export const bloqueiosService = {
  listarBloqueios: () => req('GET', '/bloqueios'),
  criarBloqueio: body => req('POST', '/bloqueios', body),
  editarBloqueio: (id, body) => req('PUT', `/bloqueios/${id}`, body),
  excluirBloqueio: id => req('DELETE', `/bloqueios/${id}`),
}
