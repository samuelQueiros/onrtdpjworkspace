export function validarForcaSenha(senha) {
  if (!senha || senha.length < 8) {
    return 'A senha deve ter pelo menos 8 caracteres.'
  }
  if (!/[A-Za-z]/.test(senha)) {
    return 'A senha deve conter pelo menos uma letra.'
  }
  if (!/\d/.test(senha)) {
    return 'A senha deve conter pelo menos um número.'
  }
  if (!/[^A-Za-z0-9]/.test(senha)) {
    return 'A senha deve conter pelo menos um caractere especial.'
  }
  return null
}
