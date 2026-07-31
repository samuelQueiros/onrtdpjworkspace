import Timeline from '../comum/Timeline'
import { formatCurrency } from '../comum/DetailFields'
import { aplicarCorrecoesSalariais } from '../../utils/historicoSalarial'

const TITULO_CAMPO = {
  cargo: 'Mudança de cargo',
  departamento: 'Mudança de departamento',
  valor_beneficios: 'Alteração de benefícios',
}

// Título usado apenas no cadastro inicial de cada campo (valor_anterior null,
// ou seja, a primeira vez que o campo é definido para o colaborador) — daí
// em diante volta a usar TITULO_CAMPO normalmente.
const TITULO_CAMPO_INICIAL = {
  cargo: 'Cargo exercido',
  departamento: 'Departamento definido para',
  valor_beneficios: 'Benefícios definidos para',
}

const TIPO_TIMELINE_CAMPO = {
  cargo: 'mudanca_cargo',
  departamento: 'mudanca_departamento',
  valor_beneficios: 'beneficio',
}

export default function LinhaDoTempoSection({ user, historicoSalarial, historicoFuncional }) {
  const eventos = []

  if (user.data_admissao) {
    eventos.push({
      data: user.data_admissao,
      criadoEm: user.data_admissao,
      titulo: 'Admissão',
      descricao: [user.cargo, user.departamento?.nome].filter(Boolean).join(' · ') || null,
      tipo: 'admissao',
    })
  }

  // "correcao" conserta o valor de um reajuste já registrado — nao e um
  // evento de carreira novo, mas o valor corrigido deve aparecer no
  // reajuste que ela corrige (ver aplicarCorrecoesSalariais). O array vem
  // ordenado do mais antigo para o mais novo, então o índice 0 é sempre o
  // cadastro inicial (só existe quando não havia salário anterior).
  aplicarCorrecoesSalariais(historicoSalarial).forEach((item, index) => {
    eventos.push({
      data: item.data_vigencia,
      criadoEm: item.criado_em,
      titulo: index === 0 ? 'Contrato salarial' : 'Reajuste salarial',
      descricao: [formatCurrency(item.salario), item.motivo].filter(Boolean).join(' · '),
      tipo: 'reajuste_salarial',
    })
  })

  for (const item of historicoFuncional || []) {
    if (item.tipo_alteracao !== 'real') continue
    const valor = item.campo === 'valor_beneficios' ? formatCurrency(item.valor_novo) : item.valor_novo
    // valor_anterior só vem null no cadastro inicial daquele campo.
    const ehCadastroInicial = item.valor_anterior === null
    const titulo = ehCadastroInicial
      ? TITULO_CAMPO_INICIAL[item.campo] || TITULO_CAMPO[item.campo] || 'Cadastro inicial'
      : TITULO_CAMPO[item.campo] || 'Alteração de cadastro'
    eventos.push({
      data: item.data_vigencia,
      criadoEm: item.criado_em,
      titulo,
      descricao: [valor, item.motivo].filter(Boolean).join(' · '),
      tipo: TIPO_TIMELINE_CAMPO[item.campo] || 'padrao',
    })
  }

  // Vários campos editados de uma vez geram registros com a mesma data_vigencia
  // (sempre "hoje", sem hora) — desempata por criado_em para o mais recente
  // ficar sempre no topo, mesmo quando a data_vigencia empata.
  eventos.sort((a, b) => (
    new Date(b.data) - new Date(a.data) || new Date(b.criadoEm) - new Date(a.criadoEm)
  ))

  return (
    <section className="card">
      <div className="card-header">
        <h2 className="card-title">Linha do tempo</h2>
      </div>
      <div className="card-body">
        <Timeline eventos={eventos} />
      </div>
    </section>
  )
}
