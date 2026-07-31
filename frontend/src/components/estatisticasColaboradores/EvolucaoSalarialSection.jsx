import SalaryLineChart from '../comum/charts/SalaryLineChart'
import { aplicarCorrecoesSalariais } from '../../utils/historicoSalarial'

export default function EvolucaoSalarialSection({ ficha, historico }) {
  // "correcao" conserta o valor de um reajuste já registrado — não é um
  // ponto novo no gráfico, mas o valor corrigido substitui o valor exibido
  // do reajuste que ela corrige (ver aplicarCorrecoesSalariais).
  const reajustes = aplicarCorrecoesSalariais(historico)

  // Usa criado_em (com hora) em vez de data_vigencia (só a data) no eixo X:
  // vários reajustes/correções no mesmo dia têm a mesma data_vigencia, o que
  // faz o eixo categórico do recharts colapsar os pontos na mesma posição e
  // o hover sempre mostrar o primeiro valor. formatDate já ignora a hora ao
  // exibir, então os rótulos continuam mostrando só dd/mm/aaaa.
  const data = reajustes.length
    ? reajustes.map(item => ({ data: item.criado_em, valor: Number(item.salario) }))
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
