import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useToast } from '../../contexts/ToastContext'
import { copiarModeloEmailFerias } from '../../utils/emailTemplates'
import { formatDate } from '../../utils/formatters'
import { DashboardIcon as Icon } from './DashboardIcons'

function AdminQuickActions({ pendentes = {} }) {
  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Atalhos rápidos</h2></div>
      <div className="card-body quick-actions">
        <Link className="quick-action" to="/aprovacoes">
          <strong>Aprovações</strong>
          <span>{pendentes.total || 0} pendente(s): {pendentes.ferias || 0} férias e {pendentes.equipamentos || 0} equipamentos.</span>
        </Link>
        <Link className="quick-action" to="/usuarios">
          <strong>Usuários</strong>
          <span>Gerenciar colaboradores.</span>
        </Link>
        <Link className="quick-action" to="/patrimonios">
          <strong>Patrimônios</strong>
          <span>Gerenciar equipamentos e vínculos.</span>
        </Link>
        <Link className="quick-action" to="/bloqueios">
          <strong>Bloqueio de datas</strong>
          <span>Impedir férias em períodos críticos.</span>
        </Link>
        <Link className="quick-action" to="/relatorios">
          <strong>Relatórios</strong>
          <span>Analise saldos por colaborador.</span>
        </Link>
        <Link className="quick-action" to="/disponibilidade">
          <strong>Calendário</strong>
          <span>Visualizar férias marcadas.</span>
        </Link>
        <Link className="quick-action" to="/configuracoes">
          <strong>Configurações</strong>
          <span>Gerencie cargos, equipes e limites.</span>
        </Link>
      </div>
    </section>
  )
}

function AdminAlertCenter({ alertas = [] }) {
  const toast = useToast()
  const [copiandoFeriasId, setCopiandoFeriasId] = useState(null)

  const copiar = async alerta => {
    setCopiandoFeriasId(alerta.ferias_id)
    try {
      await copiarModeloEmailFerias({
        ...alerta,
        ferias_usuario: alerta.nome_usuario,
        ferias_data_inicio: alerta.data_inicio,
        ferias_data_fim: alerta.data_fim,
        ferias_dias_usados: alerta.dias_usados,
      })
      toast.success('Modelo de e-mail copiado para a área de transferência.')
    } catch {
      toast.error('Não foi possível copiar o modelo automaticamente.')
    } finally {
      setCopiandoFeriasId(null)
    }
  }

  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Central de alertas</h2></div>
      <div className="card-body">
        {alertas.length > 0 ? (
          <ul className="alert-list">
            {alertas.map(alerta => (
              <li key={alerta.ferias_id} className="alert-item amber">
                <span>{Icon.alert}</span>
                <div className="alert-item-content">
                  <strong>{alerta.nome_usuario}</strong> - encaminhar à contabilidade
                  <div className="muted-xs">
                    Férias: {formatDate(alerta.data_inicio)} a {formatDate(alerta.data_fim)}
                    {alerta.dias_para_inicio === 0 ? ' (hoje!)' : ` (em ${alerta.dias_para_inicio} dia(s))`}
                  </div>
                </div>
                <button
                  className="btn btn-outline btn-sm alert-item-action"
                  type="button"
                  disabled={copiandoFeriasId === alerta.ferias_id}
                  onClick={() => copiar(alerta)}
                >
                  {copiandoFeriasId === alerta.ferias_id ? 'Copiando...' : 'Copiar modelo de e-mail'}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted p-y-8">Nenhum alerta no momento.</p>
        )}
      </div>
    </section>
  )
}

export default function AdminActionsAndAlerts({ alertas = [], pendentes = {} }) {
  return (
    <div className="grid-2">
      <AdminQuickActions pendentes={pendentes} />
      <AdminAlertCenter alertas={alertas} />
    </div>
  )
}
