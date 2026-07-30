import CompositionDonutChart from '../comum/charts/CompositionDonutChart'

export default function ComposicaoRemuneracaoSection({ ficha }) {
  const data = [
    { nome: 'Salário', valor: Number(ficha?.salario) || 0, cor: 'var(--green)' },
    { nome: 'Benefícios', valor: Number(ficha?.valor_beneficios) || 0, cor: 'var(--blue)' },
  ]

  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Composição da remuneração</h2>
      </div>
      <div className="card-body">
        <CompositionDonutChart data={data} />
      </div>
    </section>
  )
}
