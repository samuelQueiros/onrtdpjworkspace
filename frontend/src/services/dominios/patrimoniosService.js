import { req } from '../httpClient'
import { queryString } from '../../utils/queryString'

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
