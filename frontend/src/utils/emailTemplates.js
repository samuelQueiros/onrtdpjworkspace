import { formatDate } from './formatters'

export function montarModeloEmailFerias(alerta) {
  const cargo = alerta.cargo_usuario || '[Cargo]'
  const periodoInicio = alerta.ciclo_inicio ? formatDate(alerta.ciclo_inicio) : '[Data Inicial]'
  const periodoFim = alerta.ciclo_fim ? formatDate(alerta.ciclo_fim) : '[Data Final]'
  const inicioGozo = alerta.ferias_data_inicio ? formatDate(alerta.ferias_data_inicio) : '[Data]'
  const retorno = alerta.retorno_trabalho ? formatDate(alerta.retorno_trabalho) : '[Data]'
  const dias = alerta.ferias_dias_usados ?? '[Quantidade de dias]'
  const nome = alerta.ferias_usuario || '[Nome do Colaborador]'

  return `Olá, equipe da [Nome da Contabilidade ou Nome do Responsável],

Espero que estejam bem.

Solicito o processamento das férias do colaborador **${nome}**, conforme os dados abaixo:

- Cargo: ${cargo}

- Período Aquisitivo: ${periodoInicio} a ${periodoFim}

- Início do gozo: ${inicioGozo}

- Retorno ao trabalho: ${retorno}

- Dias de gozo solicitados: ${dias}

Peço que preparem os recibos de férias e confirmem o envio da documentação para assinatura.

Atenciosamente,`
}
