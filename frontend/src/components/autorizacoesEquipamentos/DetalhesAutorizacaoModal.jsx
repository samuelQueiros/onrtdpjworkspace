import { useState } from 'react'
import { StatusBadge } from '../comum/PageHelpers'
import { formatDateTime } from '../../utils/formatters'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { STATUS_AUTORIZACAO, TIPO_EQUIPAMENTO } from './statusAutorizacoes'

export default function DetalhesAutorizacaoModal({ solicitacao, onAccept, onClose, onDownload, onView }) {
  const [declaracao, setDeclaracao] = useState(false)
  const [local, setLocal] = useState('')
  const [saving, setSaving] = useState(false)
  const close = () => { if (!saving) onClose() }
  const modalRef = useModalFocusTrap(close)
  const status = STATUS_AUTORIZACAO[solicitacao.status] || { label: solicitacao.status, tone: 'gray' }
  const podeAceitar = (solicitacao.acoes_permitidas || []).includes('aceitar')

  const aceitar = async event => {
    event.preventDefault()
    if (!declaracao || !local.trim()) return
    setSaving(true)
    try {
      await onAccept(solicitacao.id, { declaracao_aceite: true, local_aceite: local.trim() })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay authorization-modal-overlay" role="presentation" onMouseDown={event => event.target === event.currentTarget && close()}>
      <div ref={modalRef} className="modal authorization-details-modal" role="dialog" aria-modal="true" aria-labelledby="authorization-details-title">
        <div className="modal-header">
          <div>
            <h2 id="authorization-details-title" className="modal-title">Autorização #{solicitacao.id}</h2>
            <StatusBadge tone={status.tone}>{status.label}</StatusBadge>
          </div>
          <button type="button" className="modal-close" onClick={close} disabled={saving} aria-label="Fechar">×</button>
        </div>

        <div className="modal-body authorization-details-body">
          <dl className="authorization-summary">
            <div><dt>Solicitada em</dt><dd>{formatDateTime(solicitacao.criado_em)}</dd></div>
            <div><dt>Aprovação</dt><dd>{formatDateTime(solicitacao.aprovado_em)}</dd></div>
            <div><dt>Rejeição</dt><dd>{formatDateTime(solicitacao.rejeitado_em)}</dd></div>
            <div><dt>Cancelamento</dt><dd>{formatDateTime(solicitacao.cancelado_em)}</dd></div>
            <div><dt>Entrega</dt><dd>{formatDateTime(solicitacao.entregue_em)}</dd></div>
            <div><dt>Aceite</dt><dd>{formatDateTime(solicitacao.aceito_em)}</dd></div>
            <div><dt>Devolução</dt><dd>{formatDateTime(solicitacao.devolvido_em)}</dd></div>
            <div><dt>Versão do termo</dt><dd>{solicitacao.termo_versao || 'A definir na entrega'}</dd></div>
          </dl>

          {solicitacao.motivo_rejeicao && (
            <div className="alert alert-error"><strong>Motivo da rejeição:</strong> {solicitacao.motivo_rejeicao}</div>
          )}
          {solicitacao.motivo_cancelamento && (
            <div className="alert alert-warning"><strong>Motivo do cancelamento:</strong> {solicitacao.motivo_cancelamento}</div>
          )}
          {solicitacao.observacoes && <p><strong>Observações:</strong> {solicitacao.observacoes}</p>}

          <section>
            <h3>Itens</h3>
            <div className="authorization-items-list">
              {solicitacao.itens.map(item => (
                <article key={item.id} className={`authorization-item status-${item.status_item}`}>
                  <strong>{TIPO_EQUIPAMENTO[item.tipo_snapshot] || item.tipo_snapshot} — {item.marca_modelo_snapshot}</strong>
                  <span>Patrimônio: {item.numero_patrimonio_snapshot || 'não informado'}</span>
                  <span>Série: {item.numero_serie_snapshot || 'não informada'}</span>
                  <span>Conservação: {item.estado_conservacao_snapshot}</span>
                  {item.motivo_remocao && <span className="text-danger">Removido: {item.motivo_remocao}</span>}
                  {item.estado_conservacao_devolucao && <span>Conservação na devolução: {item.estado_conservacao_devolucao}</span>}
                  {item.observacoes_devolucao && <span>Observações da devolução: {item.observacoes_devolucao}</span>}
                </article>
              ))}
            </div>
          </section>

          {solicitacao.devolvido_em && (
            <section>
              <h3>Registro da devolução</h3>
              <p><strong>Estado geral:</strong> {solicitacao.estado_conservacao_devolucao || 'Não informado'}</p>
              {solicitacao.itens_ausentes_devolucao && <p><strong>Itens ausentes:</strong> {solicitacao.itens_ausentes_devolucao}</p>}
              {solicitacao.observacoes_devolucao && <p><strong>Observações:</strong> {solicitacao.observacoes_devolucao}</p>}
            </section>
          )}

          {podeAceitar && (
            <form className="term-acceptance" onSubmit={aceitar}>
              <h3>Termo de responsabilidade</h3>
              <div className="term-content" tabIndex="0">
                {(solicitacao.termo_clausulas || 'O termo ainda não foi disponibilizado.').split('\n').map((linha, index) => (
                  linha ? <p key={index}>{linha}</p> : <br key={index} />
                ))}
              </div>
              <div className="alert alert-warning">
                O aceite registra evidências técnicas e a versão exibida. Ele não é apresentado pelo sistema como assinatura legal qualificada.
              </div>
              <div className="form-group">
                <label htmlFor="term-local-acceptance">Local do aceite</label>
                <input
                  id="term-local-acceptance"
                  data-autofocus
                  value={local}
                  onChange={event => setLocal(event.target.value)}
                  maxLength="180"
                  minLength="2"
                  placeholder="Ex.: Brasília/DF"
                  required
                />
              </div>
              <label className="term-confirmation">
                <input type="checkbox" checked={declaracao} onChange={event => setDeclaracao(event.target.checked)} />
                Li o termo versão {solicitacao.termo_versao} e confirmo o aceite referente aos itens entregues.
              </label>
              <button className="btn btn-primary" type="submit" disabled={!declaracao || local.trim().length < 2 || saving}>
                {saving ? 'Registrando...' : 'Registrar aceite'}
              </button>
            </form>
          )}

          {solicitacao.documento_status === 'falha' && (
            <div className="alert alert-warning">Seu aceite foi preservado, mas o PDF aguarda regeneração administrativa.</div>
          )}
        </div>

        <div className="modal-footer">
          {solicitacao.documento_id && (
            <>
              <button className="btn btn-outline" type="button" onClick={() => onView(solicitacao.documento_id)}>Visualizar termo</button>
              <button className="btn btn-outline" type="button" onClick={() => onDownload(solicitacao.documento_id, solicitacao.id)}>Baixar termo</button>
            </>
          )}
          <button className="btn btn-navy" type="button" onClick={close} disabled={saving}>Fechar</button>
        </div>
      </div>
    </div>
  )
}
