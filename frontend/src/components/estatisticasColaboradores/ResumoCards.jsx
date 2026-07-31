import StatCard from '../comum/StatCard'
import { calcularTempoDeEmpresa, formatCurrency, formatDate } from '../../utils/formatters'
import { StatIcon } from './StatIcons'

export default function ResumoCards({ user, ficha }) {
  return (
    <section className="stat-grid stat-grid-compact">
      <StatCard
        icon={<div className="stat-icon-box navy">{StatIcon.user}</div>}
        label="Nome completo"
        value={user.nome}
        sub={user.email}
      />
      <StatCard
        icon={<div className="stat-icon-box teal">{StatIcon.building}</div>}
        label="Departamento"
        value={user.departamento?.nome || 'Não informado'}
      />
      <StatCard
        icon={<div className="stat-icon-box purple">{StatIcon.briefcase}</div>}
        label="Função / Cargo"
        value={user.cargo || 'Não informado'}
      />
      <StatCard
        icon={<div className="stat-icon-box amber">{StatIcon.clock}</div>}
        label="Tempo de empresa"
        value={calcularTempoDeEmpresa(user.data_admissao)}
        sub={user.data_admissao ? `Admitido em ${formatDate(user.data_admissao)}` : null}
      />
      <StatCard
        icon={<div className="stat-icon-box green">{StatIcon.cash}</div>}
        label="Salário atual"
        value={ficha?.salario ? formatCurrency(ficha.salario) : 'Não informado'}
      />
      <StatCard
        icon={<div className="stat-icon-box teal">{StatIcon.gift}</div>}
        label="Benefícios"
        value={ficha?.valor_beneficios ? formatCurrency(ficha.valor_beneficios) : 'Não informado'}
        sub={ficha?.beneficios || null}
      />
      <StatCard
        icon={<div className="stat-icon-box navy">{StatIcon.calendar}</div>}
        label="Data de admissão"
        value={user.data_admissao ? formatDate(user.data_admissao) : 'Não informado'}
      />
    </section>
  )
}
