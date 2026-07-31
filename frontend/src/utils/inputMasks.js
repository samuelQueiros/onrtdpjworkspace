const onlyDigits = value => String(value || '').replace(/\D/g, '')

export function maskPhone(value) {
  const digits = onlyDigits(value).slice(0, 11)
  if (!digits) return ''
  if (digits.length <= 2) return `(${digits}`

  const ddd = digits.slice(0, 2)
  const number = digits.slice(2)
  const splitAt = number.length > 8 ? 5 : 4
  if (number.length <= splitAt) return `(${ddd}) ${number}`
  return `(${ddd}) ${number.slice(0, splitAt)}-${number.slice(splitAt)}`
}

export function maskCpf(value) {
  const digits = onlyDigits(value).slice(0, 11)
  if (digits.length <= 3) return digits
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9)}`
}

// Máscara de valor monetário (R$) para digitação ao vivo: trata os dígitos
// como centavos (igual a um caixa eletrônico) e formata no padrão pt-BR
// (milhar com ".", decimal com ",") a cada tecla digitada.
export function maskCurrency(value) {
  const digits = onlyDigits(value).replace(/^0+(?=\d)/, '')
  if (!digits) return ''
  const padded = digits.padStart(3, '0')
  const integerPart = padded.slice(0, -2).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  const centsPart = padded.slice(-2)
  return `${integerPart},${centsPart}`
}

// Converte o valor mascarado (ex.: "1.250,00") de volta para number (1250), para enviar à API.
export function parseCurrencyToNumber(value) {
  const digits = onlyDigits(value)
  if (!digits) return null
  return Number(digits) / 100
}

// Converte um number vindo da API (ex.: 1250.5) para o texto já mascarado (ex.: "1.250,50"),
// para exibir/editar um valor existente com a mesma máscara usada durante a digitação.
export function numberToCurrencyMask(value) {
  if (value === null || value === undefined || value === '') return ''
  const cents = Math.round(Number(value) * 100)
  if (Number.isNaN(cents)) return ''
  return maskCurrency(String(cents))
}
