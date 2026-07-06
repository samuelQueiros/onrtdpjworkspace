import { formatDateTime } from '../../utils/formatters'

export default function HistoricoAprovacao({ ferias }) {
  if (ferias.status === 'aprovada' && ferias.aprovado_por_nome) {
    return (
      <span className="historico-info green">
        ✓ {ferias.aprovado_por_nome}
        <br />
        <small>{formatDateTime(ferias.aprovado_em)}</small>
      </span>
    )
  }

  if (ferias.status === 'rejeitada' && ferias.rejeitado_por_nome) {
    return (
      <span className="historico-info red">
        ✕ {ferias.rejeitado_por_nome}
        <br />
        <small>{formatDateTime(ferias.rejeitado_em)}</small>
        {ferias.motivo_rejeicao && (
          <><br /><em>"{ferias.motivo_rejeicao}"</em></>
        )}
      </span>
    )
  }

  return <span className="muted">Aguardando</span>
}
