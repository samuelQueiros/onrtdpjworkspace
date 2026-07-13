import { req } from '../httpClient'

export const cargosService = {
  listarCargos: () => req('GET', '/cargos'),
  criarCargo: body => req('POST', '/cargos', body),
  editarCargo: (id, body) => req('PUT', `/cargos/${id}`, body),
  excluirCargo: id => req('DELETE', `/cargos/${id}`),
}
