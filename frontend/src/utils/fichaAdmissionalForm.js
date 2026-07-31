import { numberToCurrencyMask, parseCurrencyToNumber } from './inputMasks'

const CAMPOS_MONETARIOS = ['salario', 'vale_transporte', 'valor_beneficios']

export const blankFichaAdmissionalForm = {
  local_nascimento: '',
  uf_nascimento: '',
  nacionalidade: '',
  sexo: '',
  nome_mae: '',
  nome_pai: '',
  pis_numero: '',
  pis_emissao: '',
  rg_numero: '',
  rg_emissao: '',
  rg_orgao_emissor: '',
  ctps_numero: '',
  ctps_serie: '',
  ctps_validade: '',
  ctps_uf: '',
  ctps_emissao: '',
  telefone_alternativo: '',
  email_alternativo: '',
  endereco_uf: '',
  estado_civil: '',
  nome_conjuge: '',
  grau_instrucao: '',
  salario: '',
  horario_trabalho: '',
  dias_semana: '',
  vale_transporte: '',
  beneficios: '',
  valor_beneficios: '',
  contrato_experiencia_dias: '',
  status: 'rascunho',
  motivo_alteracao_salario: '',
  tipo_alteracao_salario: 'reajuste',
}

export function normalizeFicha(ficha) {
  if (!ficha) return {}
  const normalized = {}
  for (const key of Object.keys(blankFichaAdmissionalForm)) {
    const value = ficha[key]
    if (CAMPOS_MONETARIOS.includes(key)) {
      normalized[key] = numberToCurrencyMask(value)
    } else {
      normalized[key] = value === null || value === undefined ? '' : value
    }
  }
  return normalized
}

export function buildFichaPayload(form) {
  const payload = {}
  for (const [key, value] of Object.entries(form)) {
    if (key === 'contrato_experiencia_dias') {
      payload[key] = value === '' ? null : Number(value)
    } else if (CAMPOS_MONETARIOS.includes(key)) {
      payload[key] = parseCurrencyToNumber(value)
    } else if (value === '') {
      payload[key] = null
    } else {
      payload[key] = value
    }
  }
  return payload
}
