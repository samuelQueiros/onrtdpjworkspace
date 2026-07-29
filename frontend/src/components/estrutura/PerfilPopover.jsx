import { useCallback, useEffect, useState } from 'react'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { useAuth } from '../../contexts/AuthContext'
import { useToast } from '../../contexts/ToastContext'
import { api } from '../../services/api'
import { formatDate } from '../../utils/formatters'
import { maskPhone } from '../../utils/inputMasks'

const BANCARIOS_LABELS = {
  banco: 'Banco',
  agencia: 'Agência',
  conta: 'Conta',
  cpf_titular: 'CPF do titular',
  nome_titular: 'Nome do titular',
  chave_pix: 'Chave Pix',
}

const blankForm = {
  email: '',
  telefone: '',
  telefone_emergencia: '',
  telefone_emergencia_2: '',
  senha_atual: '',
  nova_senha: '',
  confirmar_senha: '',
}

export default function PerfilPopover({ onClose }) {
  const { refreshUser } = useAuth()
  const toast = useToast()
  const panelRef = useModalFocusTrap(onClose)
  const [perfil, setPerfil] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState(blankForm)
  const [mostrarBancarios, setMostrarBancarios] = useState(false)

  const carregar = useCallback(() => api.meuPerfil()
    .then(dados => {
      setPerfil(dados)
      setForm({
        email: dados.email || '',
        telefone: dados.telefone || '',
        telefone_emergencia: dados.telefone_emergencia || '',
        telefone_emergencia_2: dados.telefone_emergencia_2 || '',
        senha_atual: '',
        nova_senha: '',
        confirmar_senha: '',
      })
    })
    .catch(error => toast.error(error.message))
    .finally(() => setLoading(false)), [toast])

  useEffect(() => { carregar() }, [carregar])

  const update = changes => setForm(prev => ({ ...prev, ...changes }))

  const submit = async event => {
    event.preventDefault()
    if (form.nova_senha && form.nova_senha !== form.confirmar_senha) {
      toast.error('A confirmação de senha não corresponde à nova senha.')
      return
    }
    if (form.nova_senha && form.nova_senha.length < 8) {
      toast.error('A nova senha deve ter pelo menos 8 caracteres.')
      return
    }

    const payload = {
      email: form.email,
      telefone: form.telefone,
      telefone_emergencia: form.telefone_emergencia,
      telefone_emergencia_2: form.telefone_emergencia_2,
    }
    if (form.nova_senha) {
      payload.senha_atual = form.senha_atual
      payload.nova_senha = form.nova_senha
    }

    setSaving(true)
    try {
      const senhaAlterada = Boolean(form.nova_senha)
      await api.updateConfig(payload)
      await refreshUser()
      await carregar()
      toast.success(senhaAlterada ? 'Senha alterada com sucesso.' : 'Perfil atualizado com sucesso.')
      setForm(prev => ({ ...prev, senha_atual: '', nova_senha: '', confirmar_senha: '' }))
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const dadosBancarios = perfil?.dados_bancarios || {}
  const temDadosBancarios = Object.values(dadosBancarios).some(Boolean)

  return (
    <div
      className="perfil-popover"
      ref={panelRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="perfil-popover-title"
    >
      <div className="modal-header perfil-popover-header">
        <h2 id="perfil-popover-title" className="modal-title">Meu Perfil</h2>
        <button className="modal-close" type="button" onClick={onClose} aria-label="Fechar">×</button>
      </div>

      <div className="perfil-popover-body">
        {loading && (
          <div className="empty"><div className="spinner" /></div>
        )}

        {!loading && perfil && (
          <>
            <div className="perfil-popover-identity">
              <div className="avatar perfil-avatar" style={{ background: perfil.cor || 'var(--navy)' }}>
                {perfil.nome?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <strong>{perfil.nome}</strong>
                <div className="muted perfil-subtitle">
                  {perfil.cargo || 'Sem cargo'}{perfil.departamento?.nome ? ` · ${perfil.departamento.nome}` : ''}
                </div>
              </div>
            </div>

            <div className="perfil-readonly-row">
              <span className="credential-field-label">CPF</span>
              <span className="flex-1">{perfil.cpf || '-'}</span>
            </div>
            {perfil.data_admissao && (
              <div className="perfil-readonly-row">
                <span className="credential-field-label">Admissão</span>
                <span className="flex-1">{formatDate(perfil.data_admissao)}</span>
              </div>
            )}
            {perfil.data_aniversario && (
              <div className="perfil-readonly-row">
                <span className="credential-field-label">Aniversário</span>
                <span className="flex-1">{formatDate(perfil.data_aniversario)}</span>
              </div>
            )}

            <div className="perfil-divider" />

            <div className="inline-center gap-8">
              <span className="perfil-section-title flex-1">Dados bancários</span>
              {temDadosBancarios && (
                <button
                  className="btn btn-outline btn-sm"
                  type="button"
                  onClick={() => setMostrarBancarios(open => !open)}
                >
                  {mostrarBancarios ? 'Ocultar' : 'Mostrar'}
                </button>
              )}
            </div>
            {!temDadosBancarios && <p className="muted">Nenhum dado bancário cadastrado.</p>}
            {temDadosBancarios && mostrarBancarios && (
              <div className="stack-12">
                {Object.entries(BANCARIOS_LABELS).map(([chave, label]) => (
                  dadosBancarios[chave] ? (
                    <div className="perfil-readonly-row" key={chave}>
                      <span className="credential-field-label">{label}</span>
                      <span className="flex-1">{dadosBancarios[chave]}</span>
                    </div>
                  ) : null
                ))}
              </div>
            )}
            {temDadosBancarios && !mostrarBancarios && (
              <span className="credential-secret masked">••••••••••••</span>
            )}

            <div className="perfil-divider" />

            <form className="form-stack" onSubmit={submit}>
              <div className="form-group">
                <label htmlFor="perfil-email">E-mail</label>
                <input
                  id="perfil-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={form.email}
                  onChange={event => update({ email: event.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="perfil-telefone">Telefone</label>
                <input
                  id="perfil-telefone"
                  name="telefone"
                  type="tel"
                  inputMode="numeric"
                  maxLength="15"
                  value={maskPhone(form.telefone)}
                  onChange={event => update({ telefone: maskPhone(event.target.value) })}
                  placeholder="(00) 00000-0000"
                />
              </div>

              <div className="form-group">
                <label htmlFor="perfil-telefone-emergencia">Telefone de emergência</label>
                <input
                  id="perfil-telefone-emergencia"
                  name="telefone_emergencia"
                  type="tel"
                  inputMode="numeric"
                  maxLength="15"
                  value={maskPhone(form.telefone_emergencia)}
                  onChange={event => update({ telefone_emergencia: maskPhone(event.target.value) })}
                  placeholder="(00) 00000-0000"
                />
              </div>

              <div className="form-group">
                <label htmlFor="perfil-telefone-emergencia-2">Telefone de emergência 2</label>
                <input
                  id="perfil-telefone-emergencia-2"
                  name="telefone_emergencia_2"
                  type="tel"
                  inputMode="numeric"
                  maxLength="15"
                  value={maskPhone(form.telefone_emergencia_2)}
                  onChange={event => update({ telefone_emergencia_2: maskPhone(event.target.value) })}
                  placeholder="(00) 00000-0000"
                />
              </div>

              <div className="perfil-divider" />
              <span className="perfil-section-title">Alterar senha</span>

              <div className="form-group">
                <label htmlFor="perfil-senha-atual">Senha atual</label>
                <input
                  id="perfil-senha-atual"
                  name="senha_atual"
                  type="password"
                  autoComplete="current-password"
                  value={form.senha_atual}
                  onChange={event => update({ senha_atual: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="perfil-nova-senha">Nova senha</label>
                <input
                  id="perfil-nova-senha"
                  name="nova_senha"
                  type="password"
                  minLength="8"
                  autoComplete="new-password"
                  value={form.nova_senha}
                  onChange={event => update({ nova_senha: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="perfil-confirmar-senha">Confirmar nova senha</label>
                <input
                  id="perfil-confirmar-senha"
                  name="confirmar_senha"
                  type="password"
                  minLength="8"
                  autoComplete="new-password"
                  value={form.confirmar_senha}
                  onChange={event => update({ confirmar_senha: event.target.value })}
                />
              </div>
              <small className="form-hint">Deixe os campos de senha em branco para mantê-la inalterada.</small>

              <div className="button-row">
                <button className="btn btn-primary" type="submit" disabled={saving}>
                  {saving && <span className="inline-spinner" />}
                  Salvar alterações
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
