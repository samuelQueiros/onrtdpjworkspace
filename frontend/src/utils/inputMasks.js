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
