import { useState } from 'react'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { identificacaoEquipamento } from './patrimoniosLabels'

const ACTION_COPY = {
  vincular: {
    title: 'Vincular equipamento',
    description: 'Defina o colaborador que ficará responsável por este item.',
    submit: 'Confirmar vínculo',
    tone: 'primary',
  },
  desvincular: {
    title: 'Desvincular equipamento',
    description: 'O vínculo atual será encerrado e permanecerá disponível no histórico.',
    submit: 'Confirmar desvínculo',
    tone: 'primary',
  },
  manutencao: {
    title: 'Registrar manutenção',
    description: 'O item ficará indisponível para vínculos e solicitações até a finalização.',
    submit: 'Iniciar manutenção',
    tone: 'primary',
  },
  finalizar_manutencao: {
    title: 'Finalizar manutenção',
    description: 'Registre o serviço executado e o estado em que o item retornou.',
    submit: 'Finalizar manutenção',
    tone: 'primary',
  },
  baixa: {
    title: 'Baixar equipamento',
    description: 'O item será desativado definitivamente, mas todo o histórico será preservado.',
    submit: 'Confirmar baixa',
    tone: 'danger',
  },
}

export default function AcaoPatrimonioModal({ action, equipamento, users, saving, onClose, onSave }) {
  const [form, setForm] = useState({
    user_id: '',
    observacoes: '',
    estado_conservacao: equipamento.estado_conservacao || '',
    permitir_segunda_maquina: false,
    justificativa_excecao: '',
    motivo: '',
  })
  const modalRef = useModalFocusTrap(onClose)
  const copy = ACTION_COPY[action]
  const maquinaPrincipal = equipamento.tipo === 'notebook' || equipamento.tipo === 'desktop'
  const activeUsers = users.filter(user => user.ativo !== false)
  const update = changes => setForm(current => ({ ...current, ...changes }))

  const submit = event => {
    event.preventDefault()
    if (action === 'vincular') {
      onSave({
        user_id: Number(form.user_id),
        observacoes: form.observacoes.trim() || null,
        permitir_segunda_maquina: form.permitir_segunda_maquina,
        justificativa_excecao: form.permitir_segunda_maquina ? form.justificativa_excecao.trim() : null,
      })
      return
    }
    if (action === 'desvincular') {
      onSave({ observacoes: form.observacoes.trim() || null })
      return
    }
    if (action === 'baixa') {
      onSave({ motivo: form.motivo.trim() })
      return
    }
    onSave({
      observacoes: form.observacoes.trim(),
      estado_conservacao: form.estado_conservacao.trim() || null,
    })
  }

  return (
    <div className="modal-overlay patrimonio-modal-overlay" role="presentation" onMouseDown={event => event.target === event.currentTarget && !saving && onClose()}>
      <section ref={modalRef} className="modal patrimonio-action-modal" role="dialog" aria-modal="true" aria-labelledby="patrimonio-action-title" aria-describedby="patrimonio-action-description">
        <form onSubmit={submit}>
          <div className="modal-header">
            <div>
              <p className="patrimonio-modal-kicker">Equipamento {identificacaoEquipamento(equipamento)}</p>
              <h2 id="patrimonio-action-title" className="modal-title">{copy.title}</h2>
            </div>
            <button className="modal-close" type="button" onClick={onClose} disabled={saving} aria-label="Fechar">×</button>
          </div>

          <div className="modal-body form-stack">
            <p id="patrimonio-action-description" className="muted-sm">{copy.description}</p>

            {action === 'vincular' && (
              <>
                <div className="form-group">
                  <label htmlFor="vinculo-colaborador">Colaborador</label>
                  <select id="vinculo-colaborador" name="user_id" data-autofocus value={form.user_id} onChange={event => update({ user_id: event.target.value })} required>
                    <option value="">Selecione um colaborador</option>
                    {!activeUsers.length && <option value="" disabled>Nenhum colaborador ativo disponível</option>}
                    {activeUsers.map(user => <option key={user.id} value={user.id}>{user.nome}</option>)}
                  </select>
                </div>

                {maquinaPrincipal && (
                  <label className="patrimonio-checkbox patrimonio-checkbox-warning">
                    <input
                      type="checkbox"
                      checked={form.permitir_segunda_maquina}
                      onChange={event => update({ permitir_segunda_maquina: event.target.checked, justificativa_excecao: event.target.checked ? form.justificativa_excecao : '' })}
                    />
                    <span>
                      <strong>Permitir segunda máquina principal</strong>
                      <small>Use somente quando houver uma exceção administrativa válida.</small>
                    </span>
                  </label>
                )}

                {form.permitir_segunda_maquina && (
                  <div className="form-group">
                    <label htmlFor="vinculo-justificativa">Justificativa da exceção</label>
                    <textarea id="vinculo-justificativa" name="justificativa_excecao" value={form.justificativa_excecao} onChange={event => update({ justificativa_excecao: event.target.value })} rows="3" maxLength="1000" required />
                  </div>
                )}
              </>
            )}

            {(action === 'vincular' || action === 'desvincular') && (
              <div className="form-group">
                <label htmlFor="vinculo-observacoes">Observações</label>
                <textarea
                  id="vinculo-observacoes"
                  name="observacoes"
                  data-autofocus={action === 'desvincular' || undefined}
                  value={form.observacoes}
                  onChange={event => update({ observacoes: event.target.value })}
                  rows="3"
                  maxLength="1000"
                  placeholder="Contexto do vínculo ou desvínculo (opcional)"
                />
              </div>
            )}

            {(action === 'manutencao' || action === 'finalizar_manutencao') && (
              <>
                <div className="form-group">
                  <label htmlFor="manutencao-observacoes">{action === 'manutencao' ? 'Motivo da manutenção' : 'Serviço realizado'}</label>
                  <textarea id="manutencao-observacoes" name="observacoes" data-autofocus value={form.observacoes} onChange={event => update({ observacoes: event.target.value })} rows="4" maxLength="2000" required />
                </div>
                <div className="form-group">
                  <label htmlFor="manutencao-conservacao">Estado de conservação após o registro</label>
                  <textarea id="manutencao-conservacao" name="estado_conservacao" value={form.estado_conservacao} onChange={event => update({ estado_conservacao: event.target.value })} rows="3" maxLength="300" />
                </div>
              </>
            )}

            {action === 'baixa' && (
              <>
                <div className="alert alert-warning" role="alert">
                  A baixa não exclui registros. O equipamento não poderá receber novos vínculos ou solicitações.
                </div>
                <div className="form-group">
                  <label htmlFor="baixa-motivo">Motivo da baixa</label>
                  <textarea id="baixa-motivo" name="motivo" data-autofocus value={form.motivo} onChange={event => update({ motivo: event.target.value })} rows="4" maxLength="2000" required />
                </div>
              </>
            )}
          </div>

          <div className="modal-footer">
            <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
            <button className={copy.tone === 'danger' ? 'btn btn-danger' : 'btn btn-primary'} type="submit" disabled={saving}>
              {saving ? 'Salvando...' : copy.submit}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
