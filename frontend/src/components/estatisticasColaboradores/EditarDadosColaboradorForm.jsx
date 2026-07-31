import { useState } from 'react'
import { formatCurrency } from '../../utils/formatters'
import { maskCurrency, numberToCurrencyMask, parseCurrencyToNumber } from '../../utils/inputMasks'

export default function EditarDadosColaboradorForm({ user, ficha, cargos, departamentos, saving, onSave, onCancel }) {
  const [form, setForm] = useState({
    cargo: user.cargo || '',
    departamento_id: user.departamento_id || '',
    motivo_alteracao_funcional: '',
    tipo_alteracao_funcional: 'real',
    salario: numberToCurrencyMask(ficha?.salario),
    motivo_alteracao_salario: '',
    tipo_alteracao_salario: 'reajuste',
    valor_beneficios: numberToCurrencyMask(ficha?.valor_beneficios),
    motivo_alteracao_beneficios: '',
    tipo_alteracao_beneficios: 'real',
  })

  const update = changes => setForm(current => ({ ...current, ...changes }))

  const submit = async event => {
    event.preventDefault()

    const userPayload = {
      cargo: form.cargo || null,
      departamento_id: form.departamento_id ? Number(form.departamento_id) : null,
    }
    if (form.motivo_alteracao_funcional.trim()) {
      userPayload.motivo_alteracao_funcional = form.motivo_alteracao_funcional.trim()
      userPayload.tipo_alteracao_funcional = form.tipo_alteracao_funcional
    }

    const fichaPayload = {
      salario: parseCurrencyToNumber(form.salario),
      valor_beneficios: parseCurrencyToNumber(form.valor_beneficios),
    }
    if (form.motivo_alteracao_salario.trim()) {
      fichaPayload.motivo_alteracao_salario = form.motivo_alteracao_salario.trim()
      fichaPayload.tipo_alteracao_salario = form.tipo_alteracao_salario
    }
    if (form.motivo_alteracao_beneficios.trim()) {
      fichaPayload.motivo_alteracao_beneficios = form.motivo_alteracao_beneficios.trim()
      fichaPayload.tipo_alteracao_beneficios = form.tipo_alteracao_beneficios
    }

    try {
      await onSave({ userPayload, fichaPayload })
    } catch {
      // erro já tratado (toast) pelo componente pai; mantém o formulário aberto
    }
  }

  return (
    <form className="editar-dados-colaborador-form form-stack" onSubmit={submit}>
      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Cargo e departamento</h2>
        </div>
        <div className="card-body form-stack">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edc-cargo">Cargo</label>
              <select id="edc-cargo" value={form.cargo} onChange={event => update({ cargo: event.target.value })}>
                <option value="">Sem cargo</option>
                {cargos.map(cargo => <option key={cargo.id} value={cargo.nome}>{cargo.nome}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="edc-departamento">Departamento</label>
              <select
                id="edc-departamento"
                value={form.departamento_id}
                onChange={event => update({ departamento_id: event.target.value })}
              >
                <option value="">Sem departamento</option>
                {departamentos.map(departamento => (
                  <option key={departamento.id} value={departamento.id}>{departamento.nome}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edc-tipo-funcional">Tipo de alteração (cargo/departamento)</label>
              <select
                id="edc-tipo-funcional"
                value={form.tipo_alteracao_funcional}
                onChange={event => update({ tipo_alteracao_funcional: event.target.value })}
              >
                <option value="real">Mudança real</option>
                <option value="correcao">Correção de cadastro</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="edc-motivo-funcional">Motivo (cargo/departamento)</label>
              <input
                id="edc-motivo-funcional"
                type="text"
                maxLength="300"
                placeholder="Obrigatório só se cargo ou departamento forem alterados"
                value={form.motivo_alteracao_funcional}
                onChange={event => update({ motivo_alteracao_funcional: event.target.value })}
              />
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Salário</h2>
        </div>
        <div className="card-body form-stack">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edc-salario">Salário</label>
              <input
                id="edc-salario"
                type="text"
                inputMode="decimal"
                placeholder="0,00"
                value={form.salario}
                onChange={event => update({ salario: maskCurrency(event.target.value) })}
              />
              {ficha?.salario && <small className="form-hint">Atual: {formatCurrency(ficha.salario)}</small>}
            </div>
            <div className="form-group">
              <label htmlFor="edc-tipo-salario">Tipo de alteração (salário)</label>
              <select
                id="edc-tipo-salario"
                value={form.tipo_alteracao_salario}
                onChange={event => update({ tipo_alteracao_salario: event.target.value })}
              >
                <option value="reajuste">Reajuste (conta como aumento real)</option>
                <option value="correcao">Correção de erro de cadastro</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="edc-motivo-salario">Motivo (salário)</label>
            <input
              id="edc-motivo-salario"
              type="text"
              maxLength="300"
              placeholder="Obrigatório só se o salário for alterado"
              value={form.motivo_alteracao_salario}
              onChange={event => update({ motivo_alteracao_salario: event.target.value })}
            />
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Benefícios</h2>
        </div>
        <div className="card-body form-stack">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edc-beneficios">Valor dos benefícios</label>
              <input
                id="edc-beneficios"
                type="text"
                inputMode="decimal"
                placeholder="0,00"
                value={form.valor_beneficios}
                onChange={event => update({ valor_beneficios: maskCurrency(event.target.value) })}
              />
              {ficha?.valor_beneficios && <small className="form-hint">Atual: {formatCurrency(ficha.valor_beneficios)}</small>}
            </div>
            <div className="form-group">
              <label htmlFor="edc-tipo-beneficios">Tipo de alteração (benefícios)</label>
              <select
                id="edc-tipo-beneficios"
                value={form.tipo_alteracao_beneficios}
                onChange={event => update({ tipo_alteracao_beneficios: event.target.value })}
              >
                <option value="real">Mudança real</option>
                <option value="correcao">Correção de erro de cadastro</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="edc-motivo-beneficios">Motivo (benefícios)</label>
            <input
              id="edc-motivo-beneficios"
              type="text"
              maxLength="300"
              placeholder="Obrigatório só se o valor dos benefícios for alterado"
              value={form.motivo_alteracao_beneficios}
              onChange={event => update({ motivo_alteracao_beneficios: event.target.value })}
            />
          </div>
        </div>
      </section>

      <div className="button-row">
        <button className="btn btn-outline" type="button" onClick={onCancel} disabled={saving}>Cancelar</button>
        <button className="btn btn-primary" type="submit" disabled={saving}>
          {saving && <span className="inline-spinner" />}
          Salvar alterações
        </button>
      </div>
    </form>
  )
}
