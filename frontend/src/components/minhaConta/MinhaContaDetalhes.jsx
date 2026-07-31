import { DetailField, DetailSection } from '../comum/DetailFields'
import { formatCurrency, formatDate } from '../../utils/formatters'
import { maskCpf, maskPhone } from '../../utils/inputMasks'
import { SEXO_LABEL, ESTADO_CIVIL_LABEL } from '../../utils/fichaAdmissionalLabels'

export default function MinhaContaDetalhes({ perfil, ficha, ferias }) {
  const endereco = perfil?.endereco || {}
  const dadosBancarios = perfil?.dados_bancarios || {}

  return (
    <div className="minha-conta-body">
      <p className="muted minha-conta-hint">
        Estes dados são cadastrados e mantidos pela administração. Caso alguma informação esteja incorreta,
        entre em contato com o setor responsável.
      </p>

      <DetailSection title="Informações do trabalhador">
        <DetailField label="Nome completo" wide>{perfil.nome}</DetailField>
        <DetailField label="Data de nascimento">
          {perfil.data_aniversario ? formatDate(perfil.data_aniversario) : null}
        </DetailField>
        <DetailField label="CPF">{perfil.cpf}</DetailField>
        <DetailField label="E-mail" wide>{perfil.email}</DetailField>
      </DetailSection>

      <DetailSection title="Informações pessoais complementares">
        <DetailField label="Local de nascimento">{ficha?.local_nascimento}</DetailField>
        <DetailField label="UF de nascimento">{ficha?.uf_nascimento}</DetailField>
        <DetailField label="Nacionalidade">{ficha?.nacionalidade}</DetailField>
        <DetailField label="Sexo">{SEXO_LABEL[ficha?.sexo]}</DetailField>
        <DetailField label="Nome da mãe" wide>{ficha?.nome_mae}</DetailField>
        <DetailField label="Nome do pai" wide>{ficha?.nome_pai}</DetailField>
      </DetailSection>

      <DetailSection title="Documentos do trabalhador">
        <DetailField label="Número do PIS">{ficha?.pis_numero}</DetailField>
        <DetailField label="Emissão do PIS">{ficha?.pis_emissao ? formatDate(ficha.pis_emissao) : null}</DetailField>
        <DetailField label="Número do RG">{ficha?.rg_numero}</DetailField>
        <DetailField label="Emissão do RG">{ficha?.rg_emissao ? formatDate(ficha.rg_emissao) : null}</DetailField>
        <DetailField label="Órgão emissor do RG">{ficha?.rg_orgao_emissor}</DetailField>
        <DetailField label="Número da CTPS">{ficha?.ctps_numero}</DetailField>
        <DetailField label="Série da CTPS">{ficha?.ctps_serie}</DetailField>
        <DetailField label="Validade da CTPS">
          {ficha?.ctps_validade ? formatDate(ficha.ctps_validade) : null}
        </DetailField>
        <DetailField label="UF da CTPS">{ficha?.ctps_uf}</DetailField>
        <DetailField label="Emissão da CTPS">
          {ficha?.ctps_emissao ? formatDate(ficha.ctps_emissao) : null}
        </DetailField>
      </DetailSection>

      <DetailSection title="Dados funcionais">
        <DetailField label="Data de admissão">{perfil.data_admissao ? formatDate(perfil.data_admissao) : null}</DetailField>
        <DetailField label="Função / cargo">{perfil.cargo}</DetailField>
        <DetailField label="Departamento">{perfil.departamento?.nome}</DetailField>
        <DetailField label="Salário">{formatCurrency(ficha?.salario)}</DetailField>
        <DetailField label="Horário de trabalho">{ficha?.horario_trabalho}</DetailField>
        <DetailField label="Dias da semana">{ficha?.dias_semana}</DetailField>
        <DetailField label="Vale-transporte">{formatCurrency(ficha?.vale_transporte)}</DetailField>
        <DetailField label="Benefícios" wide>{ficha?.beneficios}</DetailField>
        <DetailField label="Valor dos benefícios">{formatCurrency(ficha?.valor_beneficios)}</DetailField>
        <DetailField label="Contrato de experiência">
          {ficha?.contrato_experiencia_dias === null || ficha?.contrato_experiencia_dias === undefined
            ? null
            : `${ficha.contrato_experiencia_dias} dia(s)`}
        </DetailField>
        <DetailField label="Status da ficha">{ficha?.status === 'completa' ? 'Completa' : 'Rascunho'}</DetailField>
      </DetailSection>

      <DetailSection title="Contato">
        <DetailField label="Telefone">{perfil.telefone ? maskPhone(perfil.telefone) : null}</DetailField>
        <DetailField label="Contato de emergência 1">
          {perfil.telefone_emergencia ? maskPhone(perfil.telefone_emergencia) : null}
        </DetailField>
        <DetailField label="Contato de emergência 2">
          {perfil.telefone_emergencia_2 ? maskPhone(perfil.telefone_emergencia_2) : null}
        </DetailField>
        <DetailField label="Telefone alternativo">
          {ficha?.telefone_alternativo ? maskPhone(ficha.telefone_alternativo) : null}
        </DetailField>
        <DetailField label="E-mail alternativo">{ficha?.email_alternativo}</DetailField>
      </DetailSection>

      <DetailSection title="Endereço">
        <DetailField label="Logradouro" wide>{endereco.logradouro}</DetailField>
        <DetailField label="Número">{endereco.numero}</DetailField>
        <DetailField label="Bairro">{endereco.bairro}</DetailField>
        <DetailField label="Cidade">{endereco.cidade}</DetailField>
        <DetailField label="UF">{ficha?.endereco_uf}</DetailField>
        <DetailField label="CEP">{endereco.cep}</DetailField>
      </DetailSection>

      <DetailSection title="Dados sociais">
        <DetailField label="Estado civil">{ESTADO_CIVIL_LABEL[ficha?.estado_civil]}</DetailField>
        <DetailField label="Nome do cônjuge" wide>{ficha?.nome_conjuge}</DetailField>
        <DetailField label="Grau de instrução" wide>{ficha?.grau_instrucao}</DetailField>
      </DetailSection>

      <DetailSection title="Dados bancários">
        <DetailField label="Banco">{dadosBancarios.banco}</DetailField>
        <DetailField label="Agência">{dadosBancarios.agencia}</DetailField>
        <DetailField label="Conta">{dadosBancarios.conta}</DetailField>
        <DetailField label="Nome do titular" wide>{dadosBancarios.nome_titular}</DetailField>
        <DetailField label="CPF do titular">
          {dadosBancarios.cpf_titular ? maskCpf(dadosBancarios.cpf_titular) : null}
        </DetailField>
        <DetailField label="Chave Pix" wide>{dadosBancarios.chave_pix}</DetailField>
      </DetailSection>

      <DetailSection title="Férias">
        <DetailField label="Direito anual">{ferias?.dias_direito_total ?? 0} dia(s)</DetailField>
        <DetailField label="Saldo atual">{ferias?.saldo ?? 0} dia(s)</DetailField>
        <DetailField label="Dias usados">{ferias?.dias_usados_total ?? 0} dia(s)</DetailField>
        <DetailField label="Próxima concessão">
          {ferias?.proxima_concessao_ferias ? formatDate(ferias.proxima_concessao_ferias) : null}
        </DetailField>
      </DetailSection>
    </div>
  )
}
