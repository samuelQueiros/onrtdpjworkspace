import { formatDate } from './formatters'

export function montarModeloEmailFerias(alerta) {
  const cargo = alerta.cargo_usuario || '[Cargo]'
  const periodoInicio = alerta.ciclo_inicio ? formatDate(alerta.ciclo_inicio) : '[Data Inicial]'
  const periodoFim = alerta.ciclo_fim ? formatDate(alerta.ciclo_fim) : '[Data Final]'
  const inicioGozo = alerta.ferias_data_inicio ? formatDate(alerta.ferias_data_inicio) : '[Data]'
  const retorno = alerta.retorno_trabalho ? formatDate(alerta.retorno_trabalho) : '[Data]'
  const dias = alerta.ferias_dias_usados ?? '[Quantidade de dias]'
  const nome = alerta.ferias_usuario || '[Nome do Colaborador]'

  return `Prezados,

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

async function copiarTexto(texto) {
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(texto)
      return
    } catch {
      // Clipboard API indisponível/negada: cai para o fallback abaixo.
    }
  }

  // Fallback para contextos sem HTTPS (ex.: acesso via IP na rede interna),
  // onde navigator.clipboard nem sequer existe.
  const textarea = document.createElement('textarea')
  textarea.value = texto
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.focus()
  textarea.select()
  try {
    if (!document.execCommand('copy')) {
      throw new Error('Não foi possível copiar automaticamente.')
    }
  } finally {
    document.body.removeChild(textarea)
  }
}

export async function copiarModeloEmailFerias(alerta) {
  await copiarTexto(montarModeloEmailFerias(alerta))
}
