import SalaryLineChart from '../comum/charts/SalaryLineChart'

export default function EvolucaoSalarialSection({ ficha }) {
  const data = ficha?.salario
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
