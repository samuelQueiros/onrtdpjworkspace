import { useState } from 'react'
import { maskPhone } from '../../utils/inputMasks'
import { SEXO_LABEL, ESTADO_CIVIL_LABEL, UF_OPTIONS } from '../../utils/fichaAdmissionalLabels'

export const blankFichaAdmissionalForm = {
  local_nascimento: '',
  uf_nascimento: '',
  nacionalidade: '',
  sexo: '',
  nome_mae: '',
  nome_pai: '',
  pis_numero: '',
  pis_emissao: '',
  rg_numero: '',
  rg_emissao: '',
  rg_orgao_emissor: '',
  ctps_numero: '',
  ctps_serie: '',
  ctps_validade: '',
  ctps_uf: '',
  ctps_emissao: '',
  telefone_alternativo: '',
  email_alternativo: '',
  endereco_uf: '',
  estado_civil: '',
  nome_conjuge: '',
  grau_instrucao: '',
  salario: '',
  horario_trabalho: '',
  dias_semana: '',
  vale_transporte: '',
  beneficios: '',
  valor_beneficios: '',
  contrato_experiencia_dias: '',
  status: 'rascunho',
}

function normalizeFicha(ficha) {
  if (!ficha) return {}
  const normalized = {}
  for (const key of Object.keys(blankFichaAdmissionalForm)) {
    const value = ficha[key]
    normalized[key] = value === null || value === undefined ? '' : value
  }
  return normalized
}

function buildPayload(form) {
  const payload = {}
  for (const [key, value] of Object.entries(form)) {
    if (key === 'contrato_experiencia_dias') {
      payload[key] = value === '' ? null : Number(value)
    } else if (value === '') {
      payload[key] = null
    } else {
      payload[key] = value
    }
  }
  return payload
}

export default function FichaAdmissionalForm({ ficha, saving, onCancel, onSubmit }) {
  const [form, setForm] = useState(() => ({ ...blankFichaAdmissionalForm, ...normalizeFicha(ficha) }))
  const [documentsOpen, setDocumentsOpen] = useState(false)
  const [socialOpen, setSocialOpen] = useState(false)
  const updateForm = changes => setForm(current => ({ ...current, ...changes }))

  const handleSubmit = event => {
    event.preventDefault()
    onSubmit(buildPayload(form))
  }

  return (
    <form className="user-modal-form" onSubmit={handleSubmit} noValidate>
      <div className="modal-header">
        <h2 id="ficha-form-title" className="modal-title">Editar ficha admissional</h2>
        <button className="modal-close" type="button" onClick={onCancel} aria-label="Fechar">×</button>
      </div>
      <div className="modal-body user-modal-body form-stack">
        <div className="form-group">
          <label htmlFor="ficha-local-nascimento">Local de nascimento</label>
          <input
            id="ficha-local-nascimento"
            type="text"
            maxLength="150"
            value={form.local_nascimento}
            onChange={event => updateForm({ local_nascimento: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-uf-nascimento">UF de nascimento</label>
          <select
            id="ficha-uf-nascimento"
            value={form.uf_nascimento}
            onChange={event => updateForm({ uf_nascimento: event.target.value })}
          >
            <option value="">Selecione</option>
            {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="ficha-nacionalidade">Nacionalidade</label>
          <input
            id="ficha-nacionalidade"
            type="text"
            maxLength="100"
            value={form.nacionalidade}
            onChange={event => updateForm({ nacionalidade: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-sexo">Sexo</label>
          <select
            id="ficha-sexo"
            value={form.sexo}
            onChange={event => updateForm({ sexo: event.target.value })}
          >
            <option value="">Selecione</option>
            {Object.entries(SEXO_LABEL).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="ficha-nome-mae">Nome da mãe</label>
          <input
            id="ficha-nome-mae"
            type="text"
            maxLength="150"
            value={form.nome_mae}
            onChange={event => updateForm({ nome_mae: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-nome-pai">Nome do pai</label>
          <input
            id="ficha-nome-pai"
            type="text"
            maxLength="150"
            value={form.nome_pai}
            onChange={event => updateForm({ nome_pai: event.target.value })}
          />
        </div>

        <div className="disclosure-field">
          <button
            className="disclosure-button"
            type="button"
            aria-expanded={documentsOpen}
            aria-controls="ficha-documents-fields"
            onClick={() => setDocumentsOpen(open => !open)}
          >
            Documentos do trabalhador
            <span className="disclosure-chevron" aria-hidden="true">{documentsOpen ? '−' : '+'}</span>
          </button>
          {documentsOpen && (
            <div id="ficha-documents-fields" className="disclosure-content form-stack">
              <div className="form-group">
                <label htmlFor="ficha-pis-numero">Número do PIS</label>
                <input
                  id="ficha-pis-numero"
                  type="text"
                  maxLength="30"
                  value={form.pis_numero}
                  onChange={event => updateForm({ pis_numero: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-pis-emissao">Emissão do PIS</label>
                <input
                  id="ficha-pis-emissao"
                  type="date"
                  value={form.pis_emissao}
                  onChange={event => updateForm({ pis_emissao: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-rg-numero">Número do RG</label>
                <input
                  id="ficha-rg-numero"
                  type="text"
                  maxLength="30"
                  value={form.rg_numero}
                  onChange={event => updateForm({ rg_numero: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-rg-emissao">Emissão do RG</label>
                <input
                  id="ficha-rg-emissao"
                  type="date"
                  value={form.rg_emissao}
                  onChange={event => updateForm({ rg_emissao: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-rg-orgao-emissor">Órgão emissor do RG</label>
                <input
                  id="ficha-rg-orgao-emissor"
                  type="text"
                  maxLength="50"
                  value={form.rg_orgao_emissor}
                  onChange={event => updateForm({ rg_orgao_emissor: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-ctps-numero">Número da CTPS</label>
                <input
                  id="ficha-ctps-numero"
                  type="text"
                  maxLength="30"
                  value={form.ctps_numero}
                  onChange={event => updateForm({ ctps_numero: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-ctps-serie">Série da CTPS</label>
                <input
                  id="ficha-ctps-serie"
                  type="text"
                  maxLength="30"
                  value={form.ctps_serie}
                  onChange={event => updateForm({ ctps_serie: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-ctps-validade">Validade da CTPS</label>
                <input
                  id="ficha-ctps-validade"
                  type="date"
                  value={form.ctps_validade}
                  onChange={event => updateForm({ ctps_validade: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-ctps-uf">UF da CTPS</label>
                <select
                  id="ficha-ctps-uf"
                  value={form.ctps_uf}
                  onChange={event => updateForm({ ctps_uf: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="ficha-ctps-emissao">Emissão da CTPS</label>
                <input
                  id="ficha-ctps-emissao"
                  type="date"
                  value={form.ctps_emissao}
                  onChange={event => updateForm({ ctps_emissao: event.target.value })}
                />
              </div>
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="ficha-salario">Salário</label>
          <input
            id="ficha-salario"
            type="text"
            inputMode="decimal"
            placeholder="0.00"
            value={form.salario}
            onChange={event => updateForm({ salario: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-horario-trabalho">Horário de trabalho</label>
          <input
            id="ficha-horario-trabalho"
            type="text"
            maxLength="150"
            value={form.horario_trabalho}
            onChange={event => updateForm({ horario_trabalho: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-dias-semana">Dias da semana</label>
          <input
            id="ficha-dias-semana"
            type="text"
            maxLength="100"
            value={form.dias_semana}
            onChange={event => updateForm({ dias_semana: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-vale-transporte">Vale-transporte</label>
          <input
            id="ficha-vale-transporte"
            type="text"
            inputMode="decimal"
            placeholder="0.00"
            value={form.vale_transporte}
            onChange={event => updateForm({ vale_transporte: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-beneficios">Benefícios</label>
          <textarea
            id="ficha-beneficios"
            maxLength="300"
            value={form.beneficios}
            onChange={event => updateForm({ beneficios: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-valor-beneficios">Valor dos benefícios</label>
          <input
            id="ficha-valor-beneficios"
            type="text"
            inputMode="decimal"
            placeholder="0.00"
            value={form.valor_beneficios}
            onChange={event => updateForm({ valor_beneficios: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-contrato-experiencia">Contrato de experiência (dias)</label>
          <input
            id="ficha-contrato-experiencia"
            type="number"
            min="0"
            max="365"
            value={form.contrato_experiencia_dias}
            onChange={event => updateForm({ contrato_experiencia_dias: event.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-status">Status da ficha</label>
          <select
            id="ficha-status"
            value={form.status}
            onChange={event => updateForm({ status: event.target.value })}
          >
            <option value="rascunho">Rascunho</option>
            <option value="completa">Completa</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="ficha-telefone-alternativo">Telefone alternativo</label>
          <input
            id="ficha-telefone-alternativo"
            type="text"
            inputMode="numeric"
            maxLength="15"
            value={maskPhone(form.telefone_alternativo)}
            onChange={event => updateForm({ telefone_alternativo: maskPhone(event.target.value) })}
            placeholder="(00) 00000-0000"
          />
        </div>
        <div className="form-group">
          <label htmlFor="ficha-email-alternativo">E-mail alternativo</label>
          <input
            id="ficha-email-alternativo"
            type="email"
            value={form.email_alternativo}
            onChange={event => updateForm({ email_alternativo: event.target.value })}
          />
        </div>

        <div className="form-group">
          <label htmlFor="ficha-endereco-uf">UF do endereço</label>
          <select
            id="ficha-endereco-uf"
            value={form.endereco_uf}
            onChange={event => updateForm({ endereco_uf: event.target.value })}
          >
            <option value="">Selecione</option>
            {UF_OPTIONS.map(uf => <option key={uf} value={uf}>{uf}</option>)}
          </select>
        </div>

        <div className="disclosure-field">
          <button
            className="disclosure-button"
            type="button"
            aria-expanded={socialOpen}
            aria-controls="ficha-social-fields"
            onClick={() => setSocialOpen(open => !open)}
          >
            Dados sociais
            <span className="disclosure-chevron" aria-hidden="true">{socialOpen ? '−' : '+'}</span>
          </button>
          {socialOpen && (
            <div id="ficha-social-fields" className="disclosure-content form-stack">
              <div className="form-group">
                <label htmlFor="ficha-estado-civil">Estado civil</label>
                <select
                  id="ficha-estado-civil"
                  value={form.estado_civil}
                  onChange={event => updateForm({ estado_civil: event.target.value })}
                >
                  <option value="">Selecione</option>
                  {Object.entries(ESTADO_CIVIL_LABEL).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="ficha-nome-conjuge">Nome do cônjuge</label>
                <input
                  id="ficha-nome-conjuge"
                  type="text"
                  maxLength="150"
                  value={form.nome_conjuge}
                  onChange={event => updateForm({ nome_conjuge: event.target.value })}
                />
              </div>
              <div className="form-group">
                <label htmlFor="ficha-grau-instrucao">Grau de instrução</label>
                <input
                  id="ficha-grau-instrucao"
                  type="text"
                  maxLength="120"
                  value={form.grau_instrucao}
                  onChange={event => updateForm({ grau_instrucao: event.target.value })}
                />
              </div>
            </div>
          )}
        </div>
      </div>
      <div className="modal-footer">
        <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving ? 'Salvando...' : 'Salvar ficha'}
        </button>
      </div>
    </form>
  )
}
