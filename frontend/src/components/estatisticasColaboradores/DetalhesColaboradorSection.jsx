import { DetailField, DetailSection } from '../comum/DetailFields'
import { calcularTempoDeEmpresa, formatCurrency, formatDate } from '../../utils/formatters'

export default function DetalhesColaboradorSection({ user, ficha }) {
  return (
    <DetailSection title="Informações detalhadas">
      <DetailField label="Nome completo" wide>{user.nome}</DetailField>
      <DetailField label="Departamento">{user.departamento?.nome}</DetailField>
      <DetailField label="Cargo">{user.cargo}</DetailField>
      <DetailField label="Data de admissão">{user.data_admissao ? formatDate(user.data_admissao) : null}</DetailField>
      <DetailField label="Tempo de empresa">{calcularTempoDeEmpresa(user.data_admissao)}</DetailField>
      <DetailField label="Salário">{ficha?.salario ? formatCurrency(ficha.salario) : null}</DetailField>
      <DetailField label="Benefício" wide>
        {ficha?.valor_beneficios
          ? `${formatCurrency(ficha.valor_beneficios)}${ficha.beneficios ? ` · ${ficha.beneficios}` : ''}`
          : null}
      </DetailField>
    </DetailSection>
  )
}
