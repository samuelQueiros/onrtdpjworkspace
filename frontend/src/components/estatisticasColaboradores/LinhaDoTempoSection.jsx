import Timeline from '../comum/Timeline'

export default function LinhaDoTempoSection({ user }) {
  const eventos = user.data_admissao
    ? [{
      data: user.data_admissao,
      titulo: 'Admissão',
      descricao: [user.cargo, user.departamento?.nome].filter(Boolean).join(' · ') || null,
      tipo: 'admissao',
    }]
    : []
  // Preparado para receber futuramente: promoções, mudanças de cargo/departamento,
  // reajustes salariais — basta adicionar novos itens a essa lista (tipo:
  // 'promocao' | 'mudanca_cargo' | 'mudanca_departamento' | 'reajuste_salarial').

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
