import { req } from '../httpClient'

export const departamentosService = {
  listarDepartamentos: () => req('GET', '/departamentos'),
  criarDepartamento: body => req('POST', '/departamentos', body),
  editarDepartamento: (id, body) => req('PUT', `/departamentos/${id}`, body),
  excluirDepartamento: id => req('DELETE', `/departamentos/${id}`),
}
