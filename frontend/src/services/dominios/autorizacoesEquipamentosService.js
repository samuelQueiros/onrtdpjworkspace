import { req } from '../httpClient'
import { queryString } from '../../utils/queryString'

export const autorizacoesEquipamentosService = {
  listarAutorizacoesAdmin: (filtros = {}) => (
    req('GET', `/autorizacoes-equipamentos/admin${queryString(filtros)}`)
  ),
  aprovarAutorizacao: (id, body) => (
    req('POST', `/autorizacoes-equipamentos/${id}/aprovar`, body)
  ),
  rejeitarAutorizacao: (id, body) => (
    req('POST', `/autorizacoes-equipamentos/${id}/rejeitar`, body)
  ),
  registrarEntregaAutorizacao: (id, body) => (
    req('POST', `/autorizacoes-equipamentos/${id}/entrega`, body)
  ),
  registrarDevolucaoAutorizacao: (id, body) => (
    req('POST', `/autorizacoes-equipamentos/${id}/devolucao`, body)
  ),
  regenerarTermoAutorizacao: id => (
    req('POST', `/autorizacoes-equipamentos/${id}/documento/regenerar`)
  ),
  criarAutorizacaoEquipamento: body => req('POST', '/autorizacoes-equipamentos', body),
  minhasAutorizacoesEquipamentos: () => req('GET', '/autorizacoes-equipamentos/me'),
  cancelarAutorizacaoEquipamento: (id, body = {}) => (
    req('POST', `/autorizacoes-equipamentos/${id}/cancelar`, body)
  ),
  aceitarAutorizacaoEquipamento: (id, body) => (
    req('POST', `/autorizacoes-equipamentos/${id}/aceite`, body)
  ),
  pendenciasAprovacoes: () => req('GET', '/aprovacoes/pendencias'),
}
