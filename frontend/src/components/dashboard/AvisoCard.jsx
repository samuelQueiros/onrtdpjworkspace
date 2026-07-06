import { formatDate } from '../../utils/formatters'

export default function AvisoCard({ aviso }) {
  return (
    <div className={`aviso-card${aviso.fixado ? ' aviso-fixado' : ''}`}>
      <div className="aviso-header">
        <strong>{aviso.titulo}</strong>
        {aviso.fixado && <span className="badge badge-amber">Fixado</span>}
      </div>
      <p className="aviso-corpo">{aviso.conteudo}</p>
      <small className="muted">
        Publicado por {aviso.criado_por_nome} em {formatDate(aviso.criado_em)}
        {aviso.data_expiracao && ` · Expira em ${formatDate(aviso.data_expiracao)}`}
      </small>
    </div>
  )
}
