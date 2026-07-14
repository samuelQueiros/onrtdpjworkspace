import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatDateTime } from '../../utils/formatters'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import {
  EVENTO_LABEL,
  STATUS_LABEL,
  STATUS_TONE,
  TIPO_LABEL,
  identificacaoEquipamento,
} from './patrimoniosLabels'

function DetailField({ label, children }) {
  return (
    <div className="patrimonio-detail-field">
      <span>{label}</span>
      <strong>{children || 'Não informado'}</strong>
    </div>
  )
}

function VinculosHistorico({ vinculos = [] }) {
  if (!vinculos.length) {
    return <EmptyState title="Nenhum vínculo registrado" text="O histórico de responsáveis aparecerá aqui." />
  }

  return (
    <div className="patrimonio-history-list">
      {vinculos.map(vinculo => (
        <article key={vinculo.id} className="patrimonio-history-item">
          <div className="patrimonio-history-marker" aria-hidden="true" />
          <div>
            <div className="patrimonio-history-heading">
              <strong>{vinculo.user_nome}</strong>
              <StatusBadge tone={vinculo.desvinculado_em ? 'gray' : 'green'}>
                {vinculo.desvinculado_em ? 'Encerrado' : 'Atual'}
              </StatusBadge>
            </div>
            <p>Vinculado em {formatDateTime(vinculo.vinculado_em)} por {vinculo.vinculado_por_nome}</p>
            {vinculo.desvinculado_em && <p>Desvinculado em {formatDateTime(vinculo.desvinculado_em)} por {vinculo.desvinculado_por_nome || 'Sistema'}</p>}
            {vinculo.maquina_principal && <p><strong>Máquina principal</strong>{vinculo.excecao_maquina_principal ? ' — exceção administrativa' : ''}</p>}
            {vinculo.justificativa_excecao && <p>Justificativa: {vinculo.justificativa_excecao}</p>}
            {vinculo.observacoes && <p>Observações: {vinculo.observacoes}</p>}
          </div>
        </article>
      ))}
    </div>
  )
}

function EventosHistorico({ eventos = [] }) {
  if (!eventos.length) {
    return <EmptyState title="Nenhum evento registrado" text="Manutenções, alterações e baixas aparecerão aqui." />
  }

  return (
    <div className="patrimonio-history-list">
      {eventos.map(evento => (
        <article key={evento.id} className="patrimonio-history-item">
          <div className="patrimonio-history-marker navy" aria-hidden="true" />
          <div>
            <div className="patrimonio-history-heading">
              <strong>{EVENTO_LABEL[evento.tipo] || evento.tipo.replaceAll('_', ' ')}</strong>
              <time dateTime={evento.criado_em}>{formatDateTime(evento.criado_em)}</time>
            </div>
            <p>Registrado por {evento.criado_por_nome}</p>
            {evento.status_anterior && evento.status_novo && (
              <p>Status: {STATUS_LABEL[evento.status_anterior] || evento.status_anterior} → {STATUS_LABEL[evento.status_novo] || evento.status_novo}</p>
            )}
            {evento.estado_conservacao && <p>Conservação: {evento.estado_conservacao}</p>}
            {evento.observacoes && <p>Observações: {evento.observacoes}</p>}
          </div>
        </article>
      ))}
    </div>
  )
}

export default function DetalhesPatrimonioModal({ equipamento, onAction, onClose, onEdit }) {
  const modalRef = useModalFocusTrap(onClose)
  const acoes = new Set(equipamento.acoes_permitidas || [])

  return (
    <div className="modal-overlay patrimonio-modal-overlay" role="presentation" onMouseDown={event => event.target === event.currentTarget && onClose()}>
      <section ref={modalRef} className="modal patrimonio-details-modal" role="dialog" aria-modal="true" aria-labelledby="patrimonio-details-title">
        <div className="modal-header">
          <div>
            <p className="patrimonio-modal-kicker">{TIPO_LABEL[equipamento.tipo] || equipamento.tipo}</p>
            <h2 id="patrimonio-details-title" className="modal-title">{identificacaoEquipamento(equipamento)} — {equipamento.marca} {equipamento.modelo}</h2>
          </div>
          <button className="modal-close" type="button" onClick={onClose} aria-label="Fechar">×</button>
        </div>

        <div className="modal-body patrimonio-details-body">
          <div className="patrimonio-detail-status-row">
            <StatusBadge tone={STATUS_TONE[equipamento.status] || 'gray'}>{STATUS_LABEL[equipamento.status] || equipamento.status}</StatusBadge>
            <StatusBadge tone={equipamento.ativo ? 'green' : 'gray'}>{equipamento.ativo ? 'Ativo' : 'Inativo'}</StatusBadge>
          </div>

          <section aria-labelledby="patrimonio-cadastro-title">
            <h3 id="patrimonio-cadastro-title" className="patrimonio-section-title">Dados do equipamento</h3>
            <div className="patrimonio-detail-grid">
              <DetailField label="Patrimônio">{equipamento.numero_patrimonio}</DetailField>
              <DetailField label="Número de série">{equipamento.numero_serie}</DetailField>
              <DetailField label="Tipo">{TIPO_LABEL[equipamento.tipo] || equipamento.tipo}</DetailField>
              <DetailField label="Marca / modelo">{equipamento.marca} {equipamento.modelo}</DetailField>
              <DetailField label="Estado de conservação">{equipamento.estado_conservacao}</DetailField>
              <DetailField label="Descrição">{equipamento.descricao}</DetailField>
            </div>
          </section>

          <section className="patrimonio-current-owner" aria-labelledby="patrimonio-vinculo-title">
            <div>
              <h3 id="patrimonio-vinculo-title" className="patrimonio-section-title">Responsável atual</h3>
              {equipamento.vinculo_atual ? (
                <>
                  <strong>{equipamento.vinculo_atual.user_nome}</strong>
                  <p>Desde {formatDateTime(equipamento.vinculo_atual.vinculado_em)}</p>
                </>
              ) : (
                <p className="muted">Este equipamento não possui vínculo ativo.</p>
              )}
            </div>
            <div className="button-row">
              {acoes.has('vincular') && <button className="btn btn-primary btn-sm" type="button" onClick={() => onAction('vincular')}>Vincular colaborador</button>}
              {acoes.has('desvincular') && <button className="btn btn-outline btn-sm" type="button" onClick={() => onAction('desvincular')}>Desvincular</button>}
            </div>
          </section>

          <section aria-labelledby="patrimonio-vinculos-history-title">
            <h3 id="patrimonio-vinculos-history-title" className="patrimonio-section-title">Histórico de vínculos</h3>
            <VinculosHistorico vinculos={equipamento.vinculos} />
          </section>

          <section aria-labelledby="patrimonio-eventos-title">
            <h3 id="patrimonio-eventos-title" className="patrimonio-section-title">Eventos do equipamento</h3>
            <EventosHistorico eventos={equipamento.eventos} />
          </section>
        </div>

        <div className="modal-footer patrimonio-details-footer">
          <div className="button-row patrimonio-operational-actions">
            {acoes.has('iniciar_manutencao') && <button className="btn btn-outline" type="button" onClick={() => onAction('manutencao')}>Registrar manutenção</button>}
            {acoes.has('finalizar_manutencao') && <button className="btn btn-primary" type="button" onClick={() => onAction('finalizar_manutencao')}>Finalizar manutenção</button>}
            {acoes.has('baixar') && <button className="btn btn-danger" type="button" onClick={() => onAction('baixa')}>Baixar equipamento</button>}
          </div>
          <div className="button-row">
            {acoes.has('editar') && <button className="btn btn-outline" type="button" onClick={onEdit}>Editar cadastro</button>}
            <button className="btn btn-navy" type="button" onClick={onClose}>Fechar</button>
          </div>
        </div>
      </section>
    </div>
  )
}
