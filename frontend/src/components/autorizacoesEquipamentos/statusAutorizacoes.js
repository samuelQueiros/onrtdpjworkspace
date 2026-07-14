export const STATUS_AUTORIZACAO = {
  pendente: { label: 'Pendente', tone: 'amber' },
  aprovada: { label: 'Aprovada', tone: 'blue' },
  aguardando_entrega: { label: 'Aguardando entrega', tone: 'blue' },
  aguardando_aceite: { label: 'Aguardando aceite', tone: 'purple' },
  aceite_registrado_aguardando_documento: { label: 'Gerando termo', tone: 'purple' },
  entregue: { label: 'Entregue e aceita', tone: 'green' },
  rejeitada: { label: 'Rejeitada', tone: 'red' },
  cancelada: { label: 'Cancelada', tone: 'gray' },
  devolvida: { label: 'Devolvida', tone: 'navy' },
}

export const TIPO_EQUIPAMENTO = {
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
