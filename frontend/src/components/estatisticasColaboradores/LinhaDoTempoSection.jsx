import Timeline from '../comum/Timeline'
import { formatCurrency } from '../comum/DetailFields'

const TITULO_CAMPO = {
  cargo: 'Mudança de cargo',
  departamento: 'Mudança de departamento',
  valor_beneficios: 'Alteração de benefícios',
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
      titulo: 'Admissão',
      descricao: [user.cargo, user.departamento?.nome].filter(Boolean).join(' · ') || null,
      tipo: 'admissao',
    })
  }

  // "correcao" conserta um valor cadastrado errado — nao e um evento de
  // carreira de verdade, entao fica fora da linha do tempo (mas continua
  // no historico para auditoria).
  for (const item of historicoSalarial || []) {
    if (item.tipo !== 'reajuste') continue
    eventos.push({
      data: item.data_vigencia,
      titulo: 'Reajuste salarial',
      descricao: [formatCurrency(item.salario), item.motivo].filter(Boolean).join(' · '),
      tipo: 'reajuste_salarial',
    })
  }

  for (const item of historicoFuncional || []) {
    if (item.tipo_alteracao !== 'real') continue
    const valor = item.campo === 'valor_beneficios' ? formatCurrency(item.valor_novo) : item.valor_novo
    eventos.push({
      data: item.data_vigencia,
      titulo: TITULO_CAMPO[item.campo] || 'Alteração de cadastro',
      descricao: [valor, item.motivo].filter(Boolean).join(' · '),
      tipo: TIPO_TIMELINE_CAMPO[item.campo] || 'padrao',
    })
  }

  eventos.sort((a, b) => new Date(b.data) - new Date(a.data))

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
