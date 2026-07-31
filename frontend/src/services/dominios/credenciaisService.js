import { req } from '../httpClient'

export const credenciaisService = {
  listarCredenciais: () => req('GET', '/credenciais'),
  criarCredencial: body => req('POST', '/credenciais', body),
  editarCredencial: (id, body) => req('PUT', `/credenciais/${id}`, body),
  excluirCredencial: id => req('DELETE', `/credenciais/${id}`),
  usuariosCredencial: id => req('GET', `/credenciais/${id}/usuarios`),
  salvarPermissoes: (id, user_ids) => req('PUT', `/credenciais/${id}/permissoes`, { user_ids }),
  minhasCredenciais: () => req('GET', '/credenciais/minhas'),
  revelarCredencial: (id, senha_atual) => req('POST', `/credenciais/${id}/revelar`, { senha_atual }),
}
