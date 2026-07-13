import { req } from '../httpClient'

export const usersService = {
  listarUsuarios: () => req('GET', '/users'),
  listarAniversariantes: () => req('GET', '/users/aniversariantes'),
  criarUsuario: body => req('POST', '/users', body),
  editarUsuario: (id, body) => req('PUT', `/users/${id}`, body),
  obterDadosSensiveisUsuario: id => req('GET', `/users/${id}/dados-sensiveis`),
  excluirUsuario: id => req('DELETE', `/users/${id}`),
  reativarUsuario: id => req('POST', `/users/${id}/reativar`),
}
