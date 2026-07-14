import { StatusBadge } from '../comum/PageHelpers'
import ModalAutorizacaoBase from './ModalAutorizacaoBase'
import {
  STATUS_AUTORIZACAO,
  STATUS_DOCUMENTO,
  STATUS_ITEM,
  descricaoItem,
  formatarDataHoraSaoPaulo,
  identificarItem,
} from './statusAutorizacoesEquipamentos'

function DetailField({ label, value }) {
  return (
    <div className="autorizacao-detail-field">
      <span>{label}</span>
      <strong>{value || '-'}</strong>
    </div>
  )
}

function eventDetails(value) {
  if (!value) return null
  try {
    const parsed = JSON.parse(value)
    return Object.entries(parsed)
      .filter(([, item]) => item !== null && item !== '' && item !== false)
      .map(([key, item]) => `${key.replaceAll('_', ' ')}: ${Array.isArray(item) ? item.join(', ') : String(item)}`)
      .join(' · ')
  } catch {
    return value
  }
}

export default function DetalhesAutorizacaoModal({ autorizacao, downloading, onClose, onDownload, onView }) {
  const status = STATUS_AUTORIZACAO[autorizacao.status] || { label: autorizacao.status, tone: 'gray' }
  const documento = STATUS_DOCUMENTO[autorizacao.documento_status] || { label: autorizacao.documento_status, tone: 'gray' }

  return (
    <ModalAutorizacaoBase
      className="autorizacao-details-modal"
      onClose={onClose}
      subtitle={`Solicitação #${autorizacao.id}`}
      title="Detalhes da autorização"
      titleId="detalhes-autorizacao-equipamento-title"
    >
      <div className="modal-body autorizacao-modal-body autorizacao-details-body">
        <div className="autorizacao-detail-status-row">
          <StatusBadge tone={status.tone}>{status.label}</StatusBadge>
          <StatusBadge tone={documento.tone}>Termo: {documento.label}</StatusBadge>
        </div>

        <section aria-labelledby="autorizacao-colaborador-heading">
          <h4 id="autorizacao-colaborador-heading" className="autorizacao-section-title">Colaborador e solicitação</h4>
          <div className="autorizacao-detail-grid">
            <DetailField label="Colaborador" value={autorizacao.user_nome} />
            <DetailField label="CPF" value={autorizacao.user_cpf_mascarado} />
            <DetailField label="Solicitado em" value={formatarDataHoraSaoPaulo(autorizacao.criado_em)} />
            <DetailField label="Tipo" value={autorizacao.tipo_solicitacao === 'item_diferente' ? 'Equipamento diferente' : 'Itens vinculados'} />
            <DetailField label="Aprovado por" value={autorizacao.aprovado_por_nome} />
            <DetailField label="Aprovado em" value={formatarDataHoraSaoPaulo(autorizacao.aprovado_em)} />
            <DetailField label="Rejeitado por" value={autorizacao.rejeitado_por_nome} />
            <DetailField label="Rejeitado em" value={formatarDataHoraSaoPaulo(autorizacao.rejeitado_em)} />
            <DetailField label="Cancelado em" value={formatarDataHoraSaoPaulo(autorizacao.cancelado_em)} />
          </div>
          {autorizacao.observacoes && <p className="autorizacao-notes"><strong>Observações:</strong> {autorizacao.observacoes}</p>}
          {autorizacao.motivo_rejeicao && <div className="alert alert-error mt-12"><span><strong>Motivo da rejeição:</strong> {autorizacao.motivo_rejeicao}</span></div>}
          {autorizacao.motivo_cancelamento && <div className="alert alert-warning mt-12"><span><strong>Motivo do cancelamento:</strong> {autorizacao.motivo_cancelamento}</span></div>}
        </section>

        <section aria-labelledby="autorizacao-itens-heading">
          <h4 id="autorizacao-itens-heading" className="autorizacao-section-title">Itens da solicitação</h4>
          <div className="autorizacao-items-list">
            {autorizacao.itens.map(item => (
              <article key={item.id} className={`autorizacao-item-card${item.status_item === 'removido' ? ' is-removed' : ''}`}>
                <div className="autorizacao-item-heading">
                  <div><strong>{identificarItem(item)}</strong><span>{descricaoItem(item)}</span></div>
                  <StatusBadge tone={item.status_item === 'removido' || item.status_item === 'ausente' ? 'red' : item.status_item === 'devolvido' ? 'gray' : 'blue'}>
                    {STATUS_ITEM[item.status_item] || item.status_item}
                  </StatusBadge>
                </div>
                <div className="autorizacao-item-meta">
                  <span><b>Série:</b> {item.numero_serie_snapshot || '-'}</span>
                  <span><b>Conservação:</b> {item.estado_conservacao_snapshot}</span>
                </div>
                {item.motivo_remocao && <p><b>Motivo da remoção:</b> {item.motivo_remocao}</p>}
                {item.estado_conservacao_devolucao && <p><b>Conservação na devolução:</b> {item.estado_conservacao_devolucao}</p>}
                {item.observacoes_devolucao && <p><b>Observações da devolução:</b> {item.observacoes_devolucao}</p>}
              </article>
            ))}
          </div>
        </section>

        {(autorizacao.entregue_em || autorizacao.aceito_em || autorizacao.devolvido_em) && (
          <section aria-labelledby="autorizacao-fluxo-heading">
            <h4 id="autorizacao-fluxo-heading" className="autorizacao-section-title">Entrega, aceite e devolução</h4>
            <div className="autorizacao-detail-grid">
              <DetailField label="Entrega registrada" value={formatarDataHoraSaoPaulo(autorizacao.entregue_em)} />
              <DetailField label="Responsável" value={autorizacao.responsavel_entrega_nome} />
              <DetailField label="Cargo do responsável" value={autorizacao.responsavel_entrega_cargo} />
              <DetailField label="Local da entrega" value={autorizacao.local_entrega} />
              <DetailField label="Aceite registrado" value={formatarDataHoraSaoPaulo(autorizacao.aceito_em)} />
              <DetailField label="Local do aceite" value={autorizacao.local_aceite} />
              <DetailField label="Devolução registrada" value={formatarDataHoraSaoPaulo(autorizacao.devolvido_em)} />
              <DetailField label="Estado geral na devolução" value={autorizacao.estado_conservacao_devolucao} />
            </div>
            {autorizacao.itens_ausentes_devolucao && <div className="alert alert-warning mt-12">Itens ausentes: {autorizacao.itens_ausentes_devolucao}</div>}
            {autorizacao.observacoes_devolucao && <p className="autorizacao-notes"><strong>Observações da devolução:</strong> {autorizacao.observacoes_devolucao}</p>}
          </section>
        )}

        {autorizacao.documento_erro && (
          <div className="alert alert-error" role="alert">
            <span><strong>Falha na geração do termo:</strong> {autorizacao.documento_erro}</span>
          </div>
        )}

        <section aria-labelledby="autorizacao-historico-heading">
          <h4 id="autorizacao-historico-heading" className="autorizacao-section-title">Histórico auditável</h4>
          {autorizacao.eventos.length ? (
            <ol className="autorizacao-timeline">
              {autorizacao.eventos.map(evento => (
                <li key={evento.id}>
                  <div className="autorizacao-timeline-marker" aria-hidden="true" />
                  <div>
                    <div className="autorizacao-timeline-heading">
                      <strong>{evento.tipo.replaceAll('_', ' ')}</strong>
                      <time dateTime={evento.criado_em}>{formatarDataHoraSaoPaulo(evento.criado_em)}</time>
                    </div>
                    <p>{evento.criado_por_nome}{evento.status_novo ? ` · status: ${STATUS_AUTORIZACAO[evento.status_novo]?.label || evento.status_novo}` : ''}</p>
                    {eventDetails(evento.detalhes) && <small>{eventDetails(evento.detalhes)}</small>}
                  </div>
                </li>
              ))}
            </ol>
          ) : <p className="muted-sm">Nenhum evento adicional registrado.</p>}
        </section>
      </div>

      <div className="modal-footer autorizacao-details-footer">
        {autorizacao.documento_id && (
          <>
            <button className="btn btn-outline" type="button" onClick={() => onView(autorizacao)} disabled={downloading}>Visualizar termo</button>
            <button className="btn btn-navy" type="button" onClick={() => onDownload(autorizacao)} disabled={downloading}>
              {downloading ? 'Processando...' : 'Baixar termo'}
            </button>
          </>
        )}
        <button className="btn btn-outline" type="button" onClick={onClose}>Fechar</button>
      </div>
    </ModalAutorizacaoBase>
  )
}
