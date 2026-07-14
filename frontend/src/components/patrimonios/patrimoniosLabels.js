export const TIPOS_EQUIPAMENTO = [
  ['notebook', 'Notebook'],
  ['desktop', 'Desktop'],
  ['monitor', 'Monitor'],
  ['mouse', 'Mouse'],
  ['teclado', 'Teclado'],
  ['headset', 'Headset'],
  ['dock_station', 'Dock station'],
  ['carregador', 'Carregador'],
  ['cabo_energia', 'Cabo de energia'],
  ['adaptador', 'Adaptador'],
  ['outro', 'Outro'],
]

export const TIPO_LABEL = Object.fromEntries(TIPOS_EQUIPAMENTO)

export const STATUS_EQUIPAMENTO = [
  ['disponivel', 'Disponível'],
  ['vinculado', 'Vinculado'],
  ['reservado', 'Reservado'],
  ['manutencao', 'Em manutenção'],
  ['baixado', 'Baixado'],
]

export const STATUS_LABEL = Object.fromEntries(STATUS_EQUIPAMENTO)

export const STATUS_TONE = {
  disponivel: 'green',
  vinculado: 'blue',
  reservado: 'amber',
  manutencao: 'purple',
  baixado: 'red',
}

export const EVENTO_LABEL = {
  criacao: 'Equipamento cadastrado',
  edicao: 'Cadastro atualizado',
  vinculo: 'Equipamento vinculado',
  desvinculo: 'Equipamento desvinculado',
  manutencao: 'Enviado para manutenção',
  manutencao_iniciada: 'Enviado para manutenção',
  manutencao_finalizada: 'Manutenção finalizada',
  baixa: 'Equipamento baixado',
  baixado: 'Equipamento baixado',
  devolucao: 'Devolução registrada',
  devolucao_ausente: 'Item ausente na devolução',
}

export function identificacaoEquipamento(equipamento) {
  return equipamento.numero_patrimonio || equipamento.numero_serie || `#${equipamento.id}`
}
