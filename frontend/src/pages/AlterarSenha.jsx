import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/pages/login.css'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'
import { validarForcaSenha } from '../utils/passwordValidation'

export default function AlterarSenha() {
  const { refreshUser } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()
  const [senhaAtual, setSenhaAtual] = useState('')
  const [novaSenha, setNovaSenha] = useState('')
  const [confirmacao, setConfirmacao] = useState('')
  const [saving, setSaving] = useState(false)

  const submit = async event => {
    event.preventDefault()
    const erroSenha = validarForcaSenha(novaSenha)
    if (erroSenha) {
      toast.error(erroSenha)
      return
    }
    if (novaSenha !== confirmacao) {
      toast.error('A confirmação não corresponde à nova senha.')
      return
    }
    if (novaSenha === senhaAtual) {
      toast.error('A nova senha deve ser diferente da senha temporária.')
      return
    }

    setSaving(true)
    try {
      await api.updateConfig({
        senha_atual: senhaAtual,
        nova_senha: novaSenha,
      })
      await refreshUser()
      toast.success('Senha definida com sucesso.')
      navigate('/', { replace: true })
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="password-change-page">
      <form className="card form-card password-change-card" onSubmit={submit}>
        <div className="card-header">
          <div>
            <h1 className="card-title">Defina sua senha</h1>
            <p className="muted">Por segurança, substitua a senha temporária antes de acessar o sistema.</p>
          </div>
        </div>
        <div className="card-body form-stack">
          <div className="form-group">
            <label htmlFor="senha-temporaria">Senha temporária</label>
            <input
              id="senha-temporaria"
              type="password"
              autoComplete="current-password"
              value={senhaAtual}
              onChange={event => setSenhaAtual(event.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="nova-senha">Nova senha</label>
            <input
              id="nova-senha"
              type="password"
              autoComplete="new-password"
              minLength="8"
              value={novaSenha}
              onChange={event => setNovaSenha(event.target.value)}
              required
            />
            <small className="form-hint">
              Mínimo de 8 caracteres, com letras, números e ao menos um caractere especial.
            </small>
          </div>
          <div className="form-group">
            <label htmlFor="confirmar-nova-senha">Confirmar nova senha</label>
            <input
              id="confirmar-nova-senha"
              type="password"
              autoComplete="new-password"
              minLength="8"
              value={confirmacao}
              onChange={event => setConfirmacao(event.target.value)}
              required
            />
          </div>
          <button className="btn btn-primary btn-lg" type="submit" disabled={saving}>
            {saving && <span className="inline-spinner" />}
            Salvar nova senha
          </button>
        </div>
      </form>
    </main>
  )
}
