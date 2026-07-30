import SalaryLineChart from '../comum/charts/SalaryLineChart'

export default function EvolucaoSalarialSection({ ficha, historico }) {
  // "correcao" conserta um valor cadastrado errado — não é um reajuste real,
  // então fica fora do gráfico (mas continua no histórico para auditoria).
  const reajustes = historico?.filter(item => item.tipo === 'reajuste') || []

  const data = reajustes.length
    ? reajustes.map(item => ({ data: item.data_vigencia, valor: Number(item.salario) }))
    : ficha?.salario
      ? [{ data: ficha.atualizado_em || ficha.criado_em, valor: Number(ficha.salario) }]
      : []

  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Evolução salarial</h2>
      </div>
      <div className="card-body">
        <SalaryLineChart data={data} />
      </div>
    </section>
  )
}
