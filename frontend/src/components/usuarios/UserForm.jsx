/* eslint-disable react-refresh/only-export-components */
import { useState } from 'react'
import ColorPicker from './ColorPicker'
import UserColorDot from './UserColorDot'
import { maskCpf, maskPhone } from '../../utils/inputMasks'

export const blankUserForm = {
  nome: '',
  email: '',
  cpf: '',
  senha: '',
  role: 'user',
  dias_totais: 30,
  departamento_id: '',
  data_admissao: '',
  data_aniversario: '',
  cor: '',
  telefone: '',
  telefone_emergencia: '',
  telefone_emergencia_2: '',
  endereco: { logradouro: '', numero: '', bairro: '', cidade: '', cep: '' },
  dados_bancarios: {
    banco: '', agencia: '', conta: '', cpf_titular: '', nome_titular: '', chave_pix: '',
  },
  cargo: '',
  saldo_inicial_dias: 30,
  saldo_atual_dias: '',
  motivo_ajuste_saldo: '',
  proxima_concessao_ferias: '',
}

export default function UserForm({
  departamentos,
  cargos,
  editing,
  form,
  onCancel,
  onChange,
  onSubmit,
}) {
  const [bankingOpen, setBankingOpen] = useState(false)
  const [addressOpen, setAddressOpen] = useState(false)
  const [validationError, setValidationError] = useState('')
  const updateForm = changes => {
    setValidationError('')
    onChange({ ...form, ...changes })
  }
  const updateBanking = changes => updateForm({
    dados_bancarios: { ...form.dados_bancarios, ...changes },
  })
  const updateAddress = changes => updateForm({
    endereco: { ...form.endereco, ...changes },
  })

  const handleSubmit = event => {
    event.preventDefault()
    const requiredFields = [
      ['Nome', form.nome, 'user-nome'],
      ['E-mail', form.email, 'user-email'],
      ['CPF', form.cpf, 'user-cpf'],
      ...(!editing ? [['Senha', form.senha, 'user-senha']] : []),
      ['Perfil', form.role, 'user-role'],
      ['Departamento', form.departamento_id, 'user-departamento'],
      ['Cargo', form.cargo, 'user-cargo'],
      ['Telefone', form.telefone, 'user-telefone'],
      ['Telefone de emergência', form.telefone_emergencia, 'user-telefone-emergencia'],
      ['Telefone de emergência 2', form.telefone_emergencia_2, 'user-telefone-emergencia-2'],
      ['Rua/Avenida', form.endereco.logradouro, 'user-logradouro', 'address'],
      ['Número', form.endereco.numero, 'user-numero', 'address'],
      ['Bairro', form.endereco.bairro, 'user-bairro', 'address'],
      ['Cidade', form.endereco.cidade, 'user-cidade', 'address'],
      ['CEP', form.endereco.cep, 'user-cep', 'address'],
      ['Banco', form.dados_bancarios.banco, 'user-banco', 'banking'],
      ['Agência', form.dados_bancarios.agencia, 'user-agencia', 'banking'],
      ['Conta', form.dados_bancarios.conta, 'user-conta', 'banking'],
      ['CPF do titular', form.dados_bancarios.cpf_titular, 'user-cpf-titular', 'banking'],
      ['Nome do titular', form.dados_bancarios.nome_titular, 'user-nome-titular', 'banking'],
      ['Chave Pix', form.dados_bancarios.chave_pix, 'user-chave-pix', 'banking'],
      ['Cor de identificação', form.cor, 'user-cor'],
      ['Dias de férias por ano', form.dias_totais, 'user-dias-totais'],
      ...(!editing ? [['Saldo atual de férias', form.saldo_inicial_dias, 'user-saldo-inicial']] : []),
      ['Data de admissão', form.data_admissao, 'user-data-admissao'],
      ['Data de aniversário', form.data_aniversario, 'user-data-aniversario'],
    ]
    const missing = requiredFields.find(([, value]) => value === '' || value === null || value === undefined)
    if (missing) {
      const [label, , fieldId, section] = missing
      if (section === 'address') setAddressOpen(true)
      if (section === 'banking') setBankingOpen(true)
      setValidationError(`O campo "${label}" deve ser preenchido.`)
      setTimeout(() => document.getElementById(fieldId)?.focus(), 0)
      return
    }
    onSubmit(event)
  }

  return (
    <form className="user-modal-form" onSubmit={handleSubmit} noValidate>
      <div className="modal-header">
        <h2 id="user-modal-title" className="modal-title">{editing ? 'Editar colaborador' : 'Cadastrar colaborador'}</h2>
        <button className="modal-close" type="button" onClick={onCancel} aria-label="Fechar">×</button>
      </div>
      <div className="modal-body user-modal-body form-stack">
        {validationError && <div className="user-form-error" role="alert">{validationError}</div>}
        <div className="form-group">
          <label htmlFor="user-nome">Nome</label>
          <input
            id="user-nome"
            name="nome"
            data-autofocus
            type="text"
            value={form.nome}
            onChange={event => updateForm({ nome: event.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="user-email">E-mail</label>
          <input
            id="user-email"
            name="email"
            autoComplete="email"
            type="email"
            value={form.email}
            onChange={event => updateForm({ email: event.target.value })}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="user-cpf">CPF do colaborador</label>
          <input
            id="user-cpf"
            name="cpf"
            inputMode="numeric"
            maxLength="14"
            value={maskCpf(form.cpf)}
            onChange={event => updateForm({ cpf: maskCpf(event.target.value) })}
            placeholder="000.000.000-00"
            autoComplete="off"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="user-senha">{editing ? 'Nova senha (deixe em branco para manter)' : 'Senha'}</label>
          <input
            id="user-senha"
            name="senha"
            autoComplete="new-password"
            type="password"
            minLength="8"
            value={form.senha}
            onChange={event => updateForm({ senha: event.target.value })}
            required={!editing}
          />
        </div>
        {!editing && (
          <div className="form-group">
            <label htmlFor="user-role">Perfil</label>
            <select id="user-role" name="role" value={form.role} onChange={event => updateForm({ role: event.target.value })} required>
              <option value="user">Usuário</option>
              <option value="admin">Administrador</option>
            </select>
          </div>
        )}
        <div className="form-group">
          <label htmlFor="user-departamento">Departamento</label>
          <select
            id="user-departamento"
            name="departamento_id"
            value={form.departamento_id}
            onChange={event => updateForm({ departamento_id: event.target.value })}
            required
          >
            <option value="">Sem departamento</option>
            {departamentos.map(departamento => (
              <option key={departamento.id} value={departamento.id}>{departamento.nome}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="user-cargo">Cargo</label>
          <select id="user-cargo" name="cargo" value={form.cargo} onChange={event => updateForm({ cargo: event.target.value })} required>
            <option value="">Selecione um cargo</option>
            {cargos.map(cargo => <option key={cargo.id} value={cargo.nome}>{cargo.nome}</option>)}
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="user-telefone">Telefone</label>
            <input
              id="user-telefone"
              name="telefone"
              autoComplete="tel"
              type="tel"
              inputMode="numeric"
              maxLength="15"
              value={maskPhone(form.telefone)}
              onChange={event => updateForm({ telefone: maskPhone(event.target.value) })}
              placeholder="(00) 00000-0000"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="user-telefone-emergencia">Telefone de emergência</label>
            <input
              id="user-telefone-emergencia"
              name="telefone_emergencia"
              type="tel"
              inputMode="numeric"
              maxLength="15"
              value={maskPhone(form.telefone_emergencia)}
              onChange={event => updateForm({ telefone_emergencia: maskPhone(event.target.value) })}
              placeholder="(00) 00000-0000"
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="user-telefone-emergencia-2">Telefone de emergência 2</label>
          <input
            id="user-telefone-emergencia-2"
            name="telefone_emergencia_2"
            type="tel"
            inputMode="numeric"
            maxLength="15"
            value={maskPhone(form.telefone_emergencia_2)}
            onChange={event => updateForm({ telefone_emergencia_2: maskPhone(event.target.value) })}
            placeholder="(00) 00000-0000"
            required
          />
        </div>

        <div className="disclosure-field">
          <button
            className="disclosure-button"
            type="button"
            aria-expanded={addressOpen}
            aria-controls="user-address-fields"
            onClick={() => setAddressOpen(open => !open)}
          >
            <span>Endereço</span>
            <span className="disclosure-chevron" aria-hidden="true">{addressOpen ? '−' : '+'}</span>
          </button>
          {addressOpen && (
            <div id="user-address-fields" className="disclosure-content form-stack">
              <div className="form-group">
                <label htmlFor="user-logradouro">Rua/Avenida</label>
                <input id="user-logradouro" name="logradouro" autoComplete="address-line1" value={form.endereco.logradouro} onChange={event => updateAddress({ logradouro: event.target.value })} placeholder='Avenida XYZ' />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="user-numero">Número</label>
                  <input id="user-numero" name="numero" value={form.endereco.numero} onChange={event => updateAddress({ numero: event.target.value })} placeholder='101' />
                </div>
                <div className="form-group">
                  <label htmlFor="user-bairro">Bairro</label>
                  <input id="user-bairro" name="bairro" value={form.endereco.bairro} onChange={event => updateAddress({ bairro: event.target.value })} placeholder='Centro' />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="user-cidade">Cidade</label>
                  <input id="user-cidade" name="cidade" autoComplete="address-level2" value={form.endereco.cidade} onChange={event => updateAddress({ cidade: event.target.value })} placeholder='Brasília' />
                </div>
                <div className="form-group">
                  <label htmlFor="user-cep">CEP</label>
                  <input id="user-cep" name="cep" autoComplete="postal-code" inputMode="numeric" maxLength="9" value={form.endereco.cep} onChange={event => updateAddress({ cep: event.target.value })} placeholder="00000-000" />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="disclosure-field">
          <button
            className="disclosure-button"
            type="button"
            aria-expanded={bankingOpen}
            aria-controls="user-banking-fields"
            onClick={() => setBankingOpen(open => !open)}
          >
            <span>Dados bancários</span>
            <span className="disclosure-chevron" aria-hidden="true">{bankingOpen ? '−' : '+'}</span>
          </button>
          {bankingOpen && (
            <div id="user-banking-fields" className="disclosure-content form-stack">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="user-banco">Banco</label>
                  <input id="user-banco" name="banco" value={form.dados_bancarios.banco} onChange={event => updateBanking({ banco: event.target.value })} placeholder="341 - Itaú" />
                </div>
                <div className="form-group">
                  <label htmlFor="user-agencia">Agência</label>
                  <input id="user-agencia" name="agencia" value={form.dados_bancarios.agencia} onChange={event => updateBanking({ agencia: event.target.value })} placeholder="0000" />
                </div>
                <div className="form-group">
                  <label htmlFor="user-conta">Conta</label>
                  <input id="user-conta" name="conta" value={form.dados_bancarios.conta} onChange={event => updateBanking({ conta: event.target.value })} placeholder="00000-0" />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="user-cpf-titular">CPF do titular</label>
                <input id="user-cpf-titular" name="cpf_titular" inputMode="numeric" maxLength="14" value={maskCpf(form.dados_bancarios.cpf_titular)} onChange={event => updateBanking({ cpf_titular: maskCpf(event.target.value) })} placeholder="000.000.000-00" />
              </div>
              <div className="form-group">
                <label htmlFor="user-nome-titular">Nome do titular</label>
                <input id="user-nome-titular" name="nome_titular" value={form.dados_bancarios.nome_titular} onChange={event => updateBanking({ nome_titular: event.target.value })} placeholder="Gabriel Hodon" />
              </div>
              <div className="form-group">
                <label htmlFor="user-chave-pix">Chave Pix</label>
                <input id="user-chave-pix" name="chave_pix" value={form.dados_bancarios.chave_pix} onChange={event => updateBanking({ chave_pix: event.target.value })} placeholder="exemplo@pix.com" />
              </div>
            </div>
          )}
        </div>

        <div className="form-group">
          <label>
            Cor de identificação
            {form.cor && (
              <span className="user-form-color-preview">
                <UserColorDot color={form.cor} size={14} />
              </span>
            )}
          </label>
          <ColorPicker value={form.cor} onChange={cor => updateForm({ cor })} />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="user-dias-totais">Dias de férias por ano</label>
            <input
              id="user-dias-totais"
              name="dias_totais"
              type="number"
              min="0"
              value={form.dias_totais}
              onChange={event => updateForm({ dias_totais: event.target.value })}
              required
            />
            <small className="form-hint">Quantidade creditada em cada nova concessão.</small>
          </div>
          <div className="form-group">
            <label htmlFor="user-data-admissao">Data de admissão</label>
            <input
              id="user-data-admissao"
              name="data_admissao"
              type="date"
              value={form.data_admissao}
              onChange={event => updateForm({ data_admissao: event.target.value })}
            />
          </div>
          <div className="form-group">
            <label htmlFor="user-proxima-concessao">Próxima concessão de férias</label>
            <input
              id="user-proxima-concessao"
              name="proxima_concessao_ferias"
              type="date"
              value={form.proxima_concessao_ferias}
              onChange={event => updateForm({ proxima_concessao_ferias: event.target.value })}
            />
            <small className="form-hint">Nesta data o sistema acrescentará a cota anual ao saldo.</small>
          </div>
          <div className="form-group">
            <label htmlFor="user-data-aniversario">Data de aniversário</label>
            <input
              id="user-data-aniversario"
              name="data_aniversario"
              type="date"
              value={form.data_aniversario}
              onChange={event => updateForm({ data_aniversario: event.target.value })}
            />
          </div>
        </div>

        {!editing && (
          <div className="form-group">
            <label htmlFor="user-saldo-inicial">Saldo atual de férias na implantação</label>
            <input
              id="user-saldo-inicial"
              name="saldo_inicial_dias"
              type="number"
              min="0"
              max="3650"
              value={form.saldo_inicial_dias}
              onChange={event => updateForm({ saldo_inicial_dias: event.target.value })}
              required
            />
            <small className="form-hint">
              Informe o saldo real disponível hoje. A admissão não recalculará férias passadas.
            </small>
          </div>
        )}

        {editing && (
          <>
            <div className="form-group">
              <label htmlFor="user-saldo-atual">Saldo atual de férias (dias)</label>
              <input
                id="user-saldo-atual"
                name="saldo_atual_dias"
                type="number"
                min="0"
                max="3650"
                value={form.saldo_atual_dias}
                onChange={event => updateForm({ saldo_atual_dias: event.target.value })}
              />
            </div>
            <div className="form-group">
              <label htmlFor="user-motivo-ajuste">Motivo do ajuste de saldo</label>
              <textarea
                id="user-motivo-ajuste"
                name="motivo_ajuste_saldo"
                rows="2"
                maxLength="500"
                value={form.motivo_ajuste_saldo}
                onChange={event => updateForm({ motivo_ajuste_saldo: event.target.value })}
                placeholder="Obrigatório somente quando o saldo for alterado"
              />
              <small className="form-hint">Todo ajuste gera uma movimentação e um registro de auditoria.</small>
            </div>
          </>
        )}

        <div className="button-row">
          <button className="btn btn-outline" type="button" onClick={onCancel}>Cancelar</button>
          <button className="btn btn-primary" type="submit">
            {editing ? 'Salvar alterações' : 'Cadastrar colaborador'}
          </button>
        </div>
      </div>
    </form>
  )
}
