import { useState } from 'react'
import { DetailField, EditableField, DetailSection, formatCurrency } from '../comum/DetailFields'
import { formatDate } from '../../utils/formatters'
import { maskCpf, maskPhone } from '../../utils/inputMasks'
import { SEXO_LABEL, ESTADO_CIVIL_LABEL, UF_OPTIONS } from '../../utils/fichaAdmissionalLabels'
import { blankFichaAdmissionalForm, normalizeFicha, buildFichaPayload } from '../../utils/fichaAdmissionalForm'

const blankEndereco = { logradouro: '', numero: '', bairro: '', cidade: '', cep: '' }
const blankDadosBancarios = { banco: '', agencia: '', conta: '', nome_titular: '', cpf_titular: '', chave_pix: '' }

const CAMPOS_FICHA_EDITAVEIS = [
  'local_nascimento', 'uf_nascimento', 'nacionalidade', 'sexo', 'nome_mae', 'nome_pai',
  'pis_numero', 'pis_emissao', 'rg_numero', 'rg_emissao', 'rg_orgao_emissor',
  'ctps_numero', 'ctps_serie', 'ctps_validade', 'ctps_uf', 'ctps_emissao',
  'telefone_alternativo', 'email_alternativo', 'endereco_uf',
  'estado_civil', 'nome_conjuge', 'grau_instrucao',
]

function normalizeSimples(base, valores) {
  const normalized = {}
  for (const key of Object.keys(base)) {
    const value = valores?.[key]
    normalized[key] = value === null || value === undefined ? '' : value
  }
  return normalized
}

export default function MinhaContaDetalhes({ perfil, ficha, ferias, saving, onSave }) {
  const [editing, setEditing] = useState(false)
  const [fichaForm, setFichaForm] = useState(blankFichaAdmissionalForm)
  const [enderecoForm, setEnderecoForm] = useState(blankEndereco)
  const [bancariosForm, setBancariosForm] = useState(blankDadosBancarios)

  const endereco = perfil?.endereco || {}
  const dadosBancarios = perfil?.dados_bancarios || {}

  const startEdit = () => {
    setFichaForm({ ...blankFichaAdmissionalForm, ...normalizeFicha(ficha) })
    setEnderecoForm(normalizeSimples(blankEndereco, endereco))
    setBancariosForm(normalizeSimples(blankDadosBancarios, dadosBancarios))
    setEditing(true)
  }
  const cancelEdit = () => setEditing(false)
  const updateFicha = changes => setFichaForm(current => ({ ...current, ...changes }))
  const updateEndereco = changes => setEnderecoForm(current => ({ ...current, ...changes }))
  const updateBancarios = changes => setBancariosForm(current => ({ ...current, ...changes }))

  const submit = async () => {
    const fichaCompleto = buildFichaPayload(fichaForm)
    const fichaPayload = {}
    for (const campo of CAMPOS_FICHA_EDITAVEIS) fichaPayload[campo] = fichaCompleto[campo]

    const enderecoPreenchido = Object.values(enderecoForm).some(valor => valor.trim())
    const bancariosPreenchido = Object.values(bancariosForm).some(valor => valor.trim())

    try {
      await onSave({
        ficha: fichaPayload,
        endereco: enderecoPreenchido ? enderecoForm : null,
        dados_bancarios: bancariosPreenchido
          ? { ...bancariosForm, cpf_titular: maskCpf(bancariosForm.cpf_titular) }
          : null,
      })
      setEditing(false)
    } catch {
      // erro já tratado (toast) pelo componente pai; mantém o formulário aberto
    }
  }

  return (
    <div className="minha-conta-body">
      <div className="minha-conta-actions">
        {editing ? (
          <>
            <button className="btn btn-outline btn-sm" type="button" onClick={cancelEdit} disabled={saving}>
              Cancelar
            </button>
            <button className="btn btn-primary btn-sm" type="button" onClick={submit} disabled={saving}>
              {saving ? 'Salvando...' : 'Salvar alterações'}
            </button>
          </>
        ) : (
          <button className="btn btn-outline btn-sm" type="button" onClick={startEdit}>
            Editar dados
          </button>
        )}
      </div>

      <DetailSection title="Informações do trabalhador">
        <DetailField label="Nome completo" wide>{perfil.nome}</DetailField>
        <DetailField label="Data de nascimento">
          {perfil.data_aniversario ? formatDate(perfil.data_aniversario) : null}
        </DetailField>
        <DetailField label="CPF">{perfil.cpf}</DetailField>
        <DetailField label="E-mail" wide>{perfil.email}</DetailField>
      </DetailSection>

      <DetailSection title="Informações pessoais complementares">
        <EditableField
          label="Local de nascimento"
          editing={editing}
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
          editing={editing}
          edit={(
            <select value={fichaForm.uf_nascimento} onChange={event => updateFicha({ uf_nascimento: event.target.value })}>
              <option value="">Selecione</option>
              {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          )}
        >
          {ficha?.uf_nascimento}
        </EditableField>
        <EditableField
          label="Nacionalidade"
          editing={editing}
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
          editing={editing}
          edit={(
            <select value={fichaForm.sexo} onChange={event => updateFicha({ sexo: event.target.value })}>
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
          editing={editing}
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
          editing={editing}
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
          editing={editing}
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
          editing={editing}
          edit={(
            <input type="date" value={fichaForm.pis_emissao} onChange={event => updateFicha({ pis_emissao: event.target.value })} />
          )}
        >
          {ficha?.pis_emissao ? formatDate(ficha.pis_emissao) : null}
        </EditableField>
        <EditableField
          label="Número do RG"
          editing={editing}
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
          editing={editing}
          edit={(
            <input type="date" value={fichaForm.rg_emissao} onChange={event => updateFicha({ rg_emissao: event.target.value })} />
          )}
        >
          {ficha?.rg_emissao ? formatDate(ficha.rg_emissao) : null}
        </EditableField>
        <EditableField
          label="Órgão emissor do RG"
          editing={editing}
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
          editing={editing}
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
          editing={editing}
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
          editing={editing}
          edit={(
            <input type="date" value={fichaForm.ctps_validade} onChange={event => updateFicha({ ctps_validade: event.target.value })} />
          )}
        >
          {ficha?.ctps_validade ? formatDate(ficha.ctps_validade) : null}
        </EditableField>
        <EditableField
          label="UF da CTPS"
          editing={editing}
          edit={(
            <select value={fichaForm.ctps_uf} onChange={event => updateFicha({ ctps_uf: event.target.value })}>
              <option value="">Selecione</option>
              {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          )}
        >
          {ficha?.ctps_uf}
        </EditableField>
        <EditableField
          label="Emissão da CTPS"
          editing={editing}
          edit={(
            <input type="date" value={fichaForm.ctps_emissao} onChange={event => updateFicha({ ctps_emissao: event.target.value })} />
          )}
        >
          {ficha?.ctps_emissao ? formatDate(ficha.ctps_emissao) : null}
        </EditableField>
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
        <p className="muted minha-conta-hint">
          Dados funcionais e financeiros são de responsabilidade da administração e não podem ser editados aqui.
        </p>
      </DetailSection>

      <DetailSection title="Contato">
        <DetailField label="Telefone">{perfil.telefone ? maskPhone(perfil.telefone) : null}</DetailField>
        <DetailField label="Contato de emergência 1">
          {perfil.telefone_emergencia ? maskPhone(perfil.telefone_emergencia) : null}
        </DetailField>
        <DetailField label="Contato de emergência 2">
          {perfil.telefone_emergencia_2 ? maskPhone(perfil.telefone_emergencia_2) : null}
        </DetailField>
        <EditableField
          label="Telefone alternativo"
          editing={editing}
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
          editing={editing}
          edit={(
            <input type="email" value={fichaForm.email_alternativo} onChange={event => updateFicha({ email_alternativo: event.target.value })} />
          )}
        >
          {ficha?.email_alternativo}
        </EditableField>
        <p className="muted minha-conta-hint">
          Para alterar telefone principal, e-mail de login ou senha, use "Meu perfil" no menu de conta.
        </p>
      </DetailSection>

      <DetailSection title="Endereço">
        <EditableField
          label="Logradouro"
          wide
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="200"
              value={enderecoForm.logradouro}
              onChange={event => updateEndereco({ logradouro: event.target.value })}
            />
          )}
        >
          {endereco.logradouro}
        </EditableField>
        <EditableField
          label="Número"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="20"
              value={enderecoForm.numero}
              onChange={event => updateEndereco({ numero: event.target.value })}
            />
          )}
        >
          {endereco.numero}
        </EditableField>
        <EditableField
          label="Bairro"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="100"
              value={enderecoForm.bairro}
              onChange={event => updateEndereco({ bairro: event.target.value })}
            />
          )}
        >
          {endereco.bairro}
        </EditableField>
        <EditableField
          label="Cidade"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="100"
              value={enderecoForm.cidade}
              onChange={event => updateEndereco({ cidade: event.target.value })}
            />
          )}
        >
          {endereco.cidade}
        </EditableField>
        <EditableField
          label="UF"
          editing={editing}
          edit={(
            <select value={fichaForm.endereco_uf} onChange={event => updateFicha({ endereco_uf: event.target.value })}>
              <option value="">Selecione</option>
              {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          )}
        >
          {ficha?.endereco_uf}
        </EditableField>
        <EditableField
          label="CEP"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="9"
              value={enderecoForm.cep}
              onChange={event => updateEndereco({ cep: event.target.value })}
              placeholder="00000-000"
            />
          )}
        >
          {endereco.cep}
        </EditableField>
      </DetailSection>

      <DetailSection title="Dados sociais">
        <EditableField
          label="Estado civil"
          editing={editing}
          edit={(
            <select value={fichaForm.estado_civil} onChange={event => updateFicha({ estado_civil: event.target.value })}>
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
          editing={editing}
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
          editing={editing}
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
        <EditableField
          label="Banco"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="100"
              value={bancariosForm.banco}
              onChange={event => updateBancarios({ banco: event.target.value })}
            />
          )}
        >
          {dadosBancarios.banco}
        </EditableField>
        <EditableField
          label="Agência"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="30"
              value={bancariosForm.agencia}
              onChange={event => updateBancarios({ agencia: event.target.value })}
            />
          )}
        >
          {dadosBancarios.agencia}
        </EditableField>
        <EditableField
          label="Conta"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="30"
              value={bancariosForm.conta}
              onChange={event => updateBancarios({ conta: event.target.value })}
            />
          )}
        >
          {dadosBancarios.conta}
        </EditableField>
        <EditableField
          label="Nome do titular"
          wide
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="150"
              value={bancariosForm.nome_titular}
              onChange={event => updateBancarios({ nome_titular: event.target.value })}
            />
          )}
        >
          {dadosBancarios.nome_titular}
        </EditableField>
        <EditableField
          label="CPF do titular"
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="14"
              value={maskCpf(bancariosForm.cpf_titular)}
              onChange={event => updateBancarios({ cpf_titular: maskCpf(event.target.value) })}
              placeholder="000.000.000-00"
            />
          )}
        >
          {dadosBancarios.cpf_titular ? maskCpf(dadosBancarios.cpf_titular) : null}
        </EditableField>
        <EditableField
          label="Chave Pix"
          wide
          editing={editing}
          edit={(
            <input
              type="text"
              maxLength="150"
              value={bancariosForm.chave_pix}
              onChange={event => updateBancarios({ chave_pix: event.target.value })}
            />
          )}
        >
          {dadosBancarios.chave_pix}
        </EditableField>
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
