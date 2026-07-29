export const STATUS_AUTORIZACAO = {
  pendente: { label: 'Pendente', tone: 'amber' },
  rejeitada: { label: 'Rejeitada', tone: 'red' },
  cancelada: { label: 'Cancelada', tone: 'gray' },
  aguardando_entrega: { label: 'Aguardando entrega', tone: 'blue' },
  aguardando_aceite: { label: 'Aguardando aceite', tone: 'purple' },
  aceite_registrado_aguardando_documento: { label: 'Gerando termo', tone: 'purple' },
  entregue: { label: 'Entregue e aceita', tone: 'green' },
  devolvida: { label: 'Devolvida', tone: 'navy' },
}

export const STATUS_DOCUMENTO = {
  pendente: { label: 'Pendente', tone: 'gray' },
  gerando: { label: 'Gerando', tone: 'amber' },
  gerado: { label: 'Disponível', tone: 'green' },
  falha: { label: 'Falha', tone: 'red' },
}

export const STATUS_ITEM = {
  solicitado: 'Solicitado',
  aprovado: 'Aprovado',
  removido: 'Removido',
  entregue: 'Entregue',
  devolvido: 'Devolvido',
  ausente: 'Ausente',
}

export const TIPOS_EQUIPAMENTO = {
  notebook: 'Notebook',
  desktop: 'Desktop',
  monitor: 'Monitor',
  mouse: 'Mouse',
  teclado: 'Teclado',
  headset: 'Headset',
  dock_station: 'Dock station',
  carregador: 'Carregador',
  cabo_energia: 'Cabo de energia',
  adaptador: 'Adaptador',
  outro: 'Outro',
}

export function identificarItem(item) {
  return item.numero_patrimonio_snapshot
    || item.numero_serie_snapshot
    || `Equipamento #${item.equipamento_id}`
}

export function descricaoItem(item) {
  const tipo = TIPOS_EQUIPAMENTO[item.tipo_snapshot] || item.tipo_snapshot
  return `${tipo} · ${item.marca_modelo_snapshot}`
}

export function formatarDataHoraSaoPaulo(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
    timeZone: 'America/Sao_Paulo',
  }).format(date)
}
