import { formatDate } from '../../utils/formatters'

export default function AvisoItem({ aviso, isAdmin, onEdit, onDelete }) {
  return (
    <div className={`aviso-card${aviso.fixado ? ' aviso-fixado' : ''}`}>
      <div className="aviso-header">
        <div className="aviso-titulo-row">
          {aviso.fixado && <span className="badge badge-amber">Fixado</span>}
          <strong>{aviso.titulo}</strong>
        </div>
        {isAdmin && (
          <div className="button-row">
            <button className="btn btn-outline btn-sm" onClick={() => onEdit(aviso)}>Editar</button>
            <button className="btn btn-danger btn-sm" onClick={() => onDelete(aviso.id)}>Excluir</button>
          </div>
        )}
      </div>
      <p className="aviso-corpo">{aviso.conteudo}</p>
      <small className="muted">
        Publicado por <strong>{aviso.criado_por_nome}</strong> em {formatDate(aviso.criado_em)}
        {aviso.data_expiracao && ` · Expira em ${formatDate(aviso.data_expiracao)}`}
      </small>
    </div>
  )
}
