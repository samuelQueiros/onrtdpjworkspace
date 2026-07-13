import { postForm, req } from '../httpClient'

export const authService = {
  login(email, senha) {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', senha)
    return postForm('/auth/session', form)
  },
  me: () => req('GET', '/auth/me'),
  logout: () => req('POST', '/auth/logout'),
  updateConfig: body => req('PUT', '/me/configuracoes', body),
}
