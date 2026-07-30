import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import { maskCpf, maskPhone } from '../../utils/inputMasks'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { SEXO_LABEL, ESTADO_CIVIL_LABEL } from '../../utils/fichaAdmissionalLabels'

function formatCurrency(value) {
  if (value === null || value === undefined || value === '') return null
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value))
}

function DetailField({ label, children, wide = false }) {
  const vazio = children === null || children === undefined || children === ''

  return (
    <div className={`user-detail-field${wide ? ' user-detail-field-wide' : ''}`}>
      <span>{label}</span>
      <strong className={vazio ? 'muted' : undefined}>{vazio ? 'Não informado' : children}</strong>
    </div>
  )
}

function DetailSection({ title, children }) {
  return (
    <section>
      <h3 className="user-detail-section-title">{title}</h3>
      <div className="user-details-grid">{children}</div>
    </section>
  )
}

export default function DetalhesUsuarioModal({
  user,
  sensitive,
  ficha,
  fichaImporting,
  fichaDownloading,
  onClose,
  onDownloadTemplate,
  onEdit,
  onEditFicha,
  onImportFicha,
}) {
  const modalRef = useModalFocusTrap(onClose)
  const endereco = sensitive?.endereco || {}
  const dadosBancarios = sensitive?.dados_bancarios || {}

  return (
    <div
      className="modal-overlay user-modal-overlay"
      role="presentation"
      onMouseDown={event => event.target === event.currentTarget && onClose()}
    >
      <section
        ref={modalRef}
        className="modal user-details-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-details-title"
      >
        <div className="modal-header">
          <div>
            <p className="user-details-kicker">Ficha admissional</p>
            <h2 id="user-details-title" className="modal-title">{user.nome}</h2>
          </div>
          <button className="modal-close" type="button" onClick={onClose} aria-label="Fechar">×</button>
        </div>

        <div className="modal-body user-details-body">
          <div className="user-detail-status-row">
            <StatusBadge tone={user.ativo ? 'green' : 'red'}>{user.ativo ? 'Ativo' : 'Inativo'}</StatusBadge>
            <StatusBadge tone={user.role === 'admin' ? 'navy' : 'gray'}>
              {user.role === 'admin' ? 'Administrador' : 'Usuário'}
            </StatusBadge>
            <StatusBadge tone={ficha?.status === 'completa' ? 'green' : 'amber'}>
              {!ficha ? 'Ficha não iniciada' : ficha.status === 'completa' ? 'Ficha completa' : 'Ficha em rascunho'}
            </StatusBadge>
          </div>

          <section className="user-details-import-panel" aria-labelledby="user-ficha-import-title">
            <div>
              <h3 id="user-ficha-import-title">Importação da ficha admissional</h3>
              <p>Baixe o modelo deste colaborador, preencha os dados complementares e importe o arquivo aqui.</p>
            </div>
            <div className="button-row">
              <button
                className="btn btn-outline btn-sm"
                type="button"
                onClick={onDownloadTemplate}
                disabled={fichaDownloading || fichaImporting}
              >
                {fichaDownloading ? 'Baixando...' : 'Baixar modelo Excel'}
              </button>
              <label className={`btn btn-primary btn-sm clickable-label${fichaImporting ? ' disabled' : ''}`}>
                {fichaImporting ? 'Importando...' : 'Importar Excel'}
                <input
                  type="file"
                  accept=".xlsx"
                  className="hidden-input"
                  disabled={fichaImporting || fichaDownloading}
                  onChange={event => {
                    const file = event.target.files?.[0]
                    if (file) onImportFicha(file)
                    event.target.value = ''
                  }}
                />
              </label>
            </div>
          </section>

          <DetailSection title="Informações do trabalhador">
            <DetailField label="Nome completo" wide>{user.nome}</DetailField>
            <DetailField label="Data de nascimento">{user.data_aniversario ? formatDate(user.data_aniversario) : null}</DetailField>
            <DetailField label="CPF">{sensitive?.cpf ? maskCpf(sensitive.cpf) : user.cpf_mascarado}</DetailField>
            <DetailField label="E-mail" wide>{user.email}</DetailField>
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
            <DetailField label="Validade da CTPS">{ficha?.ctps_validade ? formatDate(ficha.ctps_validade) : null}</DetailField>
            <DetailField label="UF da CTPS">{ficha?.ctps_uf}</DetailField>
            <DetailField label="Emissão da CTPS">{ficha?.ctps_emissao ? formatDate(ficha.ctps_emissao) : null}</DetailField>
          </DetailSection>

          <DetailSection title="Dados funcionais">
            <DetailField label="Data de admissão">{user.data_admissao ? formatDate(user.data_admissao) : null}</DetailField>
            <DetailField label="Função / cargo">{user.cargo}</DetailField>
            <DetailField label="Departamento">{user.departamento?.nome}</DetailField>
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
          </DetailSection>

          <DetailSection title="Contato">
            <DetailField label="Telefone">{user.telefone ? maskPhone(user.telefone) : null}</DetailField>
            <DetailField label="Telefone alternativo">
              {ficha?.telefone_alternativo ? maskPhone(ficha.telefone_alternativo) : null}
            </DetailField>
            <DetailField label="E-mail alternativo">{ficha?.email_alternativo}</DetailField>
            <DetailField label="Contato de emergência 1">
              {sensitive?.telefone_emergencia ? maskPhone(sensitive.telefone_emergencia) : null}
            </DetailField>
            <DetailField label="Contato de emergência 2">
              {sensitive?.telefone_emergencia_2 ? maskPhone(sensitive.telefone_emergencia_2) : null}
            </DetailField>
          </DetailSection>

          <DetailSection title="Endereço do trabalhador">
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
            <DetailField label="Direito anual">{user.dias_totais} dia(s)</DetailField>
            <DetailField label="Saldo atual">{user.dias_restantes} dia(s)</DetailField>
            <DetailField label="Dias usados">{user.dias_usados_total ?? 0} dia(s)</DetailField>
            <DetailField label="Próxima concessão">
              {user.proxima_concessao_ferias ? formatDate(user.proxima_concessao_ferias) : null}
            </DetailField>
          </DetailSection>
        </div>

        <div className="modal-footer user-details-footer">
          <button className="btn btn-outline" type="button" onClick={onEditFicha}>Editar ficha admissional</button>
          <button className="btn btn-outline" type="button" onClick={onEdit}>Editar cadastro</button>
          <button className="btn btn-navy" type="button" onClick={onClose}>Fechar</button>
        </div>
      </section>
    </div>
  )
}
