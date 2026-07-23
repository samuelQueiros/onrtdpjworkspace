import { formatDate } from '../../utils/formatters'

export default function DiasVencidosAlert({ vencidas }) {
  if (!vencidas || vencidas.length === 0) return null

  return (
    <div className="vencidas-stack">
      {vencidas.map(vencida => (
        <div className="alert alert-warning vencida-card" key={vencida.ano_referencia}>
          <div>
            <strong>Férias vencidas referente ao Ano {vencida.ano_referencia}</strong>
            <div>
              {vencida.dias} dia(s) não utilizados do período de {formatDate(vencida.ciclo_inicio)} a {formatDate(vencida.ciclo_fim)}.
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
