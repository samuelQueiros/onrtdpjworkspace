import { Fragment, useEffect, useState } from 'react'
import '../styles/pages/lembretes-ferias.css'
import { EmptyState, LoadingCard, PageHeader, StatusBadge } from '../components/comum/PageHelpers'
import { STATUS_ENVIO } from '../components/lembretesFerias/statusEnvios'
import { useToast } from '../contexts/ToastContext'
import { formatDateTime } from '../utils/formatters'
import { api } from '../services/api'

const POLL_MS = 45000

export default function LembretesFerias() {
  const toast = useToast()
  const [envios, setEnvios] = useState([])
  const [loading, setLoading] = useState(true)
  const [expandidoId, setExpandidoId] = useState(null)

  useEffect(() => {
    const carregar = () => api.listarEnvios()
      .then(setEnvios)
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false))

    carregar()
    window.addEventListener('lembretes-ferias:changed', carregar)
    const intervalId = window.setInterval(carregar, POLL_MS)
    return () => {
      window.removeEventListener('lembretes-ferias:changed', carregar)
      window.clearInterval(intervalId)
    }
  }, [toast])

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Lembretes de Férias"
        subtitle="Histórico dos e-mails automáticos de aviso de férias enviados à contabilidade."
      />

      <section className="card">
        {envios.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Colaborador</th>
                  <th>Período</th>
                  <th>Status</th>
                  <th>Enviado em</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {envios.map(envio => {
                  const status = STATUS_ENVIO[envio.status] || { label: envio.status, tone: 'gray' }
                  const expandido = expandidoId === envio.id
                  return (
                    <Fragment key={envio.id}>
                      <tr>
                        <td><strong>{envio.colaborador_nome_snapshot}</strong></td>
                        <td>{envio.periodo_ferias_snapshot || '-'}</td>
                        <td>
                          <StatusBadge tone={status.tone}>{status.label}</StatusBadge>
                          {envio.lido_em && <span className="lembrete-lido-selo">Aberto pelo destinatário</span>}
                        </td>
                        <td>{formatDateTime(envio.enviado_em)}</td>
                        <td className="actions-cell">
                          {envio.status === 'respondido' && (
                            <button
                              className="btn btn-outline btn-sm"
                              type="button"
                              onClick={() => setExpandidoId(expandido ? null : envio.id)}
                            >
                              {expandido ? 'Ocultar resposta' : 'Ver resposta'}
                            </button>
                          )}
                          {envio.status === 'erro_definitivo' && envio.erro_mensagem && (
                            <span className="lembrete-erro-mensagem">{envio.erro_mensagem}</span>
                          )}
                        </td>
                      </tr>
                      {expandido && (
                        <tr>
                          <td colSpan={5}>
                            <div className="lembrete-resposta-texto">{envio.resposta_texto}</div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState
            title="Nenhum lembrete enviado ainda"
            text="Envie um aviso de férias a partir do modal de notificação para começar o histórico."
          />
        )}
      </section>
    </>
  )
}
