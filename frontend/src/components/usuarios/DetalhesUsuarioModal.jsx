import { useState } from 'react'
import { StatusBadge } from '../comum/PageHelpers'
import { formatDate } from '../../utils/formatters'
import { maskCpf, maskPhone } from '../../utils/inputMasks'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { SEXO_LABEL, ESTADO_CIVIL_LABEL, UF_OPTIONS } from '../../utils/fichaAdmissionalLabels'
import { blankFichaAdmissionalForm, normalizeFicha, buildFichaPayload } from '../../utils/fichaAdmissionalForm'

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

function EditableField({ label, wide = false, editing, edit, children }) {
  if (editing) {
    return (
      <div className={`user-detail-field${wide ? ' user-detail-field-wide' : ''}`}>
        <span>{label}</span>
        {edit}
      </div>
    )
  }
  return <DetailField label={label} wide={wide}>{children}</DetailField>
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
  fichaSaving,
  onClose,
  onDownloadTemplate,
  onEdit,
  onImportFicha,
  onSaveFicha,
}) {
  const modalRef = useModalFocusTrap(onClose)
  const endereco = sensitive?.endereco || {}
  const dadosBancarios = sensitive?.dados_bancarios || {}
  const [editingFicha, setEditingFicha] = useState(false)
  const [fichaForm, setFichaForm] = useState(blankFichaAdmissionalForm)

  const startEditFicha = () => {
    setFichaForm({ ...blankFichaAdmissionalForm, ...normalizeFicha(ficha) })
    setEditingFicha(true)
  }
  const cancelEditFicha = () => setEditingFicha(false)
  const updateFicha = changes => setFichaForm(current => ({ ...current, ...changes }))

  const submitFicha = async () => {
    try {
      await onSaveFicha(buildFichaPayload(fichaForm))
      setEditingFicha(false)
    } catch {
      // erro já tratado (toast) pelo componente pai; mantém o formulário aberto
    }
  }

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
              <h3 id="user-ficha-import-title">Ficha admissional</h3>
              <p>
                {editingFicha
                  ? 'Edite os campos abaixo e clique em Salvar.'
                  : 'Baixe o modelo, importe uma planilha preenchida ou edite os dados diretamente.'}
              </p>
            </div>
            <div className="button-row">
              {editingFicha ? (
                <>
                  <button
                    className="btn btn-outline btn-sm"
                    type="button"
                    onClick={cancelEditFicha}
                    disabled={fichaSaving}
                  >
                    Cancelar
                  </button>
                  <button
                    className="btn btn-primary btn-sm"
                    type="button"
                    onClick={submitFicha}
                    disabled={fichaSaving}
                  >
                    {fichaSaving ? 'Salvando...' : 'Salvar'}
                  </button>
                </>
              ) : (
                <>
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
                  <button className="btn btn-outline btn-sm" type="button" onClick={startEditFicha}>
                    Editar
                  </button>
                </>
              )}
            </div>
          </section>

          <DetailSection title="Informações do trabalhador">
            <DetailField label="Nome completo" wide>{user.nome}</DetailField>
            <DetailField label="Data de nascimento">{user.data_aniversario ? formatDate(user.data_aniversario) : null}</DetailField>
            <DetailField label="CPF">{sensitive?.cpf ? maskCpf(sensitive.cpf) : user.cpf_mascarado}</DetailField>
            <DetailField label="E-mail" wide>{user.email}</DetailField>
          </DetailSection>

          <DetailSection title="Informações pessoais complementares">
            <EditableField
              label="Local de nascimento"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="150"
                  value={fichaForm.local_nascimento}
                  onChange={event => updateFicha({ local_nascimento: event.target.value })}
                />
              )}
            >
              {ficha?.local_nascimento}
            </EditableField>
            <EditableField
              label="UF de nascimento"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.uf_nascimento}
                  onChange={event => updateFicha({ uf_nascimento: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
                </select>
              )}
            >
              {ficha?.uf_nascimento}
            </EditableField>
            <EditableField
              label="Nacionalidade"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="100"
                  value={fichaForm.nacionalidade}
                  onChange={event => updateFicha({ nacionalidade: event.target.value })}
                />
              )}
            >
              {ficha?.nacionalidade}
            </EditableField>
            <EditableField
              label="Sexo"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.sexo}
                  onChange={event => updateFicha({ sexo: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {Object.entries(SEXO_LABEL).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              )}
            >
              {SEXO_LABEL[ficha?.sexo]}
            </EditableField>
            <EditableField
              label="Nome da mãe"
              wide
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="150"
                  value={fichaForm.nome_mae}
                  onChange={event => updateFicha({ nome_mae: event.target.value })}
                />
              )}
            >
              {ficha?.nome_mae}
            </EditableField>
            <EditableField
              label="Nome do pai"
              wide
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="150"
                  value={fichaForm.nome_pai}
                  onChange={event => updateFicha({ nome_pai: event.target.value })}
                />
              )}
            >
              {ficha?.nome_pai}
            </EditableField>
          </DetailSection>

          <DetailSection title="Documentos do trabalhador">
            <EditableField
              label="Número do PIS"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="30"
                  value={fichaForm.pis_numero}
                  onChange={event => updateFicha({ pis_numero: event.target.value })}
                />
              )}
            >
              {ficha?.pis_numero}
            </EditableField>
            <EditableField
              label="Emissão do PIS"
              editing={editingFicha}
              edit={(
                <input
                  type="date"
                  value={fichaForm.pis_emissao}
                  onChange={event => updateFicha({ pis_emissao: event.target.value })}
                />
              )}
            >
              {ficha?.pis_emissao ? formatDate(ficha.pis_emissao) : null}
            </EditableField>
            <EditableField
              label="Número do RG"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="30"
                  value={fichaForm.rg_numero}
                  onChange={event => updateFicha({ rg_numero: event.target.value })}
                />
              )}
            >
              {ficha?.rg_numero}
            </EditableField>
            <EditableField
              label="Emissão do RG"
              editing={editingFicha}
              edit={(
                <input
                  type="date"
                  value={fichaForm.rg_emissao}
                  onChange={event => updateFicha({ rg_emissao: event.target.value })}
                />
              )}
            >
              {ficha?.rg_emissao ? formatDate(ficha.rg_emissao) : null}
            </EditableField>
            <EditableField
              label="Órgão emissor do RG"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="50"
                  value={fichaForm.rg_orgao_emissor}
                  onChange={event => updateFicha({ rg_orgao_emissor: event.target.value })}
                />
              )}
            >
              {ficha?.rg_orgao_emissor}
            </EditableField>
            <EditableField
              label="Número da CTPS"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="30"
                  value={fichaForm.ctps_numero}
                  onChange={event => updateFicha({ ctps_numero: event.target.value })}
                />
              )}
            >
              {ficha?.ctps_numero}
            </EditableField>
            <EditableField
              label="Série da CTPS"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="30"
                  value={fichaForm.ctps_serie}
                  onChange={event => updateFicha({ ctps_serie: event.target.value })}
                />
              )}
            >
              {ficha?.ctps_serie}
            </EditableField>
            <EditableField
              label="Validade da CTPS"
              editing={editingFicha}
              edit={(
                <input
                  type="date"
                  value={fichaForm.ctps_validade}
                  onChange={event => updateFicha({ ctps_validade: event.target.value })}
                />
              )}
            >
              {ficha?.ctps_validade ? formatDate(ficha.ctps_validade) : null}
            </EditableField>
            <EditableField
              label="UF da CTPS"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.ctps_uf}
                  onChange={event => updateFicha({ ctps_uf: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
                </select>
              )}
            >
              {ficha?.ctps_uf}
            </EditableField>
            <EditableField
              label="Emissão da CTPS"
              editing={editingFicha}
              edit={(
                <input
                  type="date"
                  value={fichaForm.ctps_emissao}
                  onChange={event => updateFicha({ ctps_emissao: event.target.value })}
                />
              )}
            >
              {ficha?.ctps_emissao ? formatDate(ficha.ctps_emissao) : null}
            </EditableField>
          </DetailSection>

          <DetailSection title="Dados funcionais">
            <DetailField label="Data de admissão">{user.data_admissao ? formatDate(user.data_admissao) : null}</DetailField>
            <DetailField label="Função / cargo">{user.cargo}</DetailField>
            <DetailField label="Departamento">{user.departamento?.nome}</DetailField>
            <EditableField
              label="Salário"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  inputMode="decimal"
                  placeholder="0.00"
                  value={fichaForm.salario}
                  onChange={event => updateFicha({ salario: event.target.value })}
                />
              )}
            >
              {formatCurrency(ficha?.salario)}
            </EditableField>
            <EditableField
              label="Horário de trabalho"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="150"
                  value={fichaForm.horario_trabalho}
                  onChange={event => updateFicha({ horario_trabalho: event.target.value })}
                />
              )}
            >
              {ficha?.horario_trabalho}
            </EditableField>
            <EditableField
              label="Dias da semana"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="100"
                  value={fichaForm.dias_semana}
                  onChange={event => updateFicha({ dias_semana: event.target.value })}
                />
              )}
            >
              {ficha?.dias_semana}
            </EditableField>
            <EditableField
              label="Vale-transporte"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  inputMode="decimal"
                  placeholder="0.00"
                  value={fichaForm.vale_transporte}
                  onChange={event => updateFicha({ vale_transporte: event.target.value })}
                />
              )}
            >
              {formatCurrency(ficha?.vale_transporte)}
            </EditableField>
            <EditableField
              label="Benefícios"
              wide
              editing={editingFicha}
              edit={(
                <textarea
                  maxLength="300"
                  value={fichaForm.beneficios}
                  onChange={event => updateFicha({ beneficios: event.target.value })}
                />
              )}
            >
              {ficha?.beneficios}
            </EditableField>
            <EditableField
              label="Valor dos benefícios"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  inputMode="decimal"
                  placeholder="0.00"
                  value={fichaForm.valor_beneficios}
                  onChange={event => updateFicha({ valor_beneficios: event.target.value })}
                />
              )}
            >
              {formatCurrency(ficha?.valor_beneficios)}
            </EditableField>
            <EditableField
              label="Contrato de experiência"
              editing={editingFicha}
              edit={(
                <input
                  type="number"
                  min="0"
                  max="365"
                  value={fichaForm.contrato_experiencia_dias}
                  onChange={event => updateFicha({ contrato_experiencia_dias: event.target.value })}
                />
              )}
            >
              {ficha?.contrato_experiencia_dias === null || ficha?.contrato_experiencia_dias === undefined
                ? null
                : `${ficha.contrato_experiencia_dias} dia(s)`}
            </EditableField>
            <EditableField
              label="Status da ficha"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.status}
                  onChange={event => updateFicha({ status: event.target.value })}
                >
                  <option value="rascunho">Rascunho</option>
                  <option value="completa">Completa</option>
                </select>
              )}
            >
              {ficha?.status === 'completa' ? 'Completa' : 'Rascunho'}
            </EditableField>
          </DetailSection>

          <DetailSection title="Contato">
            <DetailField label="Telefone">{user.telefone ? maskPhone(user.telefone) : null}</DetailField>
            <EditableField
              label="Telefone alternativo"
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  inputMode="numeric"
                  maxLength="15"
                  value={maskPhone(fichaForm.telefone_alternativo)}
                  onChange={event => updateFicha({ telefone_alternativo: maskPhone(event.target.value) })}
                  placeholder="(00) 00000-0000"
                />
              )}
            >
              {ficha?.telefone_alternativo ? maskPhone(ficha.telefone_alternativo) : null}
            </EditableField>
            <EditableField
              label="E-mail alternativo"
              editing={editingFicha}
              edit={(
                <input
                  type="email"
                  value={fichaForm.email_alternativo}
                  onChange={event => updateFicha({ email_alternativo: event.target.value })}
                />
              )}
            >
              {ficha?.email_alternativo}
            </EditableField>
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
            <EditableField
              label="UF"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.endereco_uf}
                  onChange={event => updateFicha({ endereco_uf: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
                </select>
              )}
            >
              {ficha?.endereco_uf}
            </EditableField>
            <DetailField label="CEP">{endereco.cep}</DetailField>
          </DetailSection>

          <DetailSection title="Dados sociais">
            <EditableField
              label="Estado civil"
              editing={editingFicha}
              edit={(
                <select
                  value={fichaForm.estado_civil}
                  onChange={event => updateFicha({ estado_civil: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {Object.entries(ESTADO_CIVIL_LABEL).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              )}
            >
              {ESTADO_CIVIL_LABEL[ficha?.estado_civil]}
            </EditableField>
            <EditableField
              label="Nome do cônjuge"
              wide
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="150"
                  value={fichaForm.nome_conjuge}
                  onChange={event => updateFicha({ nome_conjuge: event.target.value })}
                />
              )}
            >
              {ficha?.nome_conjuge}
            </EditableField>
            <EditableField
              label="Grau de instrução"
              wide
              editing={editingFicha}
              edit={(
                <input
                  type="text"
                  maxLength="120"
                  value={fichaForm.grau_instrucao}
                  onChange={event => updateFicha({ grau_instrucao: event.target.value })}
                />
              )}
            >
              {ficha?.grau_instrucao}
            </EditableField>
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
          <button className="btn btn-outline" type="button" onClick={onEdit}>Editar cadastro</button>
          <button className="btn btn-navy" type="button" onClick={onClose}>Fechar</button>
        </div>
      </section>
    </div>
  )
}
