import { req } from '../httpClient'

function queryString(params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      query.set(key, String(value))
    }
  })
  const encoded = query.toString()
  return encoded ? `?${encoded}` : ''
}

export const patrimoniosService = {
  listarEquipamentos: (params = {}) => req('GET', `/patrimonios${queryString(params)}`),
  obterEquipamento: id => req('GET', `/patrimonios/${id}`),
  criarEquipamento: body => req('POST', '/patrimonios', body),
  editarEquipamento: (id, body) => req('PUT', `/patrimonios/${id}`, body),
  vincularEquipamento: (id, body) => req('POST', `/patrimonios/${id}/vinculos`, body),
  desvincularEquipamento: (id, body) => req('POST', `/patrimonios/${id}/desvincular`, body),
  registrarManutencao: (id, body) => req('POST', `/patrimonios/${id}/manutencao`, body),
  finalizarManutencao: (id, body) => req('POST', `/patrimonios/${id}/finalizar-manutencao`, body),
  baixarEquipamento: (id, body) => req('POST', `/patrimonios/${id}/baixa`, body),
  meusPatrimonios: () => req('GET', '/patrimonios/me'),
  patrimoniosDisponiveis: () => req('GET', '/patrimonios/disponiveis'),
}
