import { req } from '../httpClient'

export const configuracaoService = {
  obterConfiguracao: () => req('GET', '/configuracao'),
  atualizarConfiguracao: body => req('PUT', '/configuracao', body),
}
