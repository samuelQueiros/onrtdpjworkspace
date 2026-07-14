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
