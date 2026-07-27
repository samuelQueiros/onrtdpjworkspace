import { formatDate } from '../../utils/formatters'

const LABELS = {
  saldo_inicial: 'Saldo inicial',
  credito_anual: 'Crédito anual',
  ajuste_manual: 'Ajuste administrativo',
}

export default function ExtratoSaldoFerias({ movimentos = [] }) {
  return (
    <section className="card">
      <div className="card-header"><h2 className="card-title">Extrato do saldo</h2></div>
      <div className="table-wrap">
        {movimentos.length ? (
          <table>
            <thead>
              <tr><th>Data</th><th>Movimentação</th><th>Motivo</th><th>Dias</th></tr>
            </thead>
            <tbody>
              {movimentos.map((movimento, index) => (
                <tr key={`${movimento.tipo}-${movimento.criado_em}-${index}`}>
                  <td>{formatDate(movimento.data_referencia)}</td>
                  <td>{LABELS[movimento.tipo] || movimento.tipo}</td>
                  <td>{movimento.motivo || '-'}</td>
                  <td><strong>{movimento.quantidade_dias > 0 ? '+' : ''}{movimento.quantidade_dias}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <div className="empty"><p>Nenhuma movimentação registrada.</p></div>}
      </div>
    </section>
  )
}
