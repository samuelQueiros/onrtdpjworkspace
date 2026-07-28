import { EmptyState, StatusBadge } from '../comum/PageHelpers'
import { formatBytes, formatDate } from '../../utils/formatters'
import { TIPO_LABEL, TIPO_TONE } from './documentosLabels'

export default function DocumentosTabela({
  docs,
  aba,
  isAdmin,
  loading,
  escopoRecebidos,
  onDelete,
  onDownload,
  onAbaChange,
  onEscopoRecebidosChange,
  onUserFilter,
  selectedUser,
  users,
}) {
  return (
    <section className="card">
      <div className="card-header documents-header">
        <div>
          <h2 className="card-title">Histórico de documentos</h2>
          <div className="documents-tabs" role="tablist" aria-label="Histórico de documentos">
            <button
              type="button"
              className={`documents-tab ${aba === 'recebidos' ? 'active' : ''}`}
              onClick={() => onAbaChange('recebidos')}
              role="tab"
              aria-selected={aba === 'recebidos'}
            >
              Documentos recebidos
            </button>
            <button
              type="button"
              className={`documents-tab ${aba === 'enviados' ? 'active' : ''}`}
              onClick={() => onAbaChange('enviados')}
              role="tab"
              aria-selected={aba === 'enviados'}
            >
              Documentos enviados
            </button>
          </div>
          {aba === 'recebidos' && isAdmin && (
            <div className="documents-scope" aria-label="Tipo de caixa recebida">
              <button
                type="button"
                className={escopoRecebidos === 'pessoal' ? 'active' : ''}
                onClick={() => onEscopoRecebidosChange('pessoal')}
              >
                Pessoal
              </button>
              <button
                type="button"
                className={escopoRecebidos === 'administracao' ? 'active' : ''}
                onClick={() => onEscopoRecebidosChange('administracao')}
              >
                Administração
              </button>
            </div>
          )}
        </div>
        {isAdmin && !(aba === 'recebidos' && escopoRecebidos === 'pessoal') && (
          <select
            value={selectedUser}
            onChange={event => onUserFilter(event.target.value)}
            className="select-filter"
          >
            <option value="">Todos os colaboradores</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>{user.nome}</option>
            ))}
          </select>
        )}
      </div>

      <div className="table-wrap">
        {loading ? (
          <div className="empty"><div className="spinner" /><p>Carregando...</p></div>
        ) : docs.length ? (
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Arquivo</th>
                <th>Tamanho</th>
                <th>{aba === 'recebidos' ? 'Enviado por' : 'Enviado para'}</th>
                <th>Data</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id}>
                  <td>
                    <StatusBadge tone={TIPO_TONE[doc.tipo] || 'gray'}>
                      {TIPO_LABEL[doc.tipo] || doc.tipo}
                    </StatusBadge>
                  </td>
                  <td>{doc.nome_arquivo}</td>
                  <td>{formatBytes(doc.tamanho)}</td>
                  <td>{aba === 'recebidos' ? doc.criado_por_nome : doc.destinatario_nome}</td>
                  <td>{formatDate(doc.criado_em)}</td>
                  <td className="actions-cell">
                    <button className="btn btn-outline btn-sm" onClick={() => onDownload(doc.id)}>
                      Download
                    </button>
                    {isAdmin && (
                      <button className="btn btn-danger btn-sm" onClick={() => onDelete(doc.id)}>
                        Excluir
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState
            title={`Nenhum documento ${aba === 'recebidos' ? 'recebido' : 'enviado'}`}
            text={selectedUser ? 'Nenhum documento encontrado para o colaborador selecionado.' : 'Ainda não há documentos nesta caixa.'}
          />
        )}
      </div>
    </section>
  )
}
