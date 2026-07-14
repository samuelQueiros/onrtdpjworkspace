import { useEffect, useState } from 'react'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { TIPOS_EQUIPAMENTO } from './patrimoniosLabels'

const blankForm = {
  numero_patrimonio: '',
  numero_serie: '',
  tipo: 'notebook',
  marca: '',
  modelo: '',
  descricao: '',
  estado_conservacao: '',
  ativo: true,
}

function formFromEquipment(equipamento) {
  if (!equipamento) return blankForm
  return {
    numero_patrimonio: equipamento.numero_patrimonio || '',
    numero_serie: equipamento.numero_serie || '',
    tipo: equipamento.tipo || 'notebook',
    marca: equipamento.marca || '',
    modelo: equipamento.modelo || '',
    descricao: equipamento.descricao || '',
    estado_conservacao: equipamento.estado_conservacao || '',
    ativo: equipamento.ativo !== false,
  }
}

export default function EquipamentoModal({ equipamento, saving, onClose, onSave }) {
  const editing = Boolean(equipamento)
  const [form, setForm] = useState(() => formFromEquipment(equipamento))
  const modalRef = useModalFocusTrap(onClose)

  useEffect(() => setForm(formFromEquipment(equipamento)), [equipamento])

  const update = changes => setForm(current => ({ ...current, ...changes }))
  const submit = event => {
    event.preventDefault()
    onSave({
      numero_patrimonio: form.numero_patrimonio.trim() || null,
      numero_serie: form.numero_serie.trim() || null,
      tipo: form.tipo,
      marca: form.marca.trim(),
      modelo: form.modelo.trim(),
      descricao: form.descricao.trim() || null,
      estado_conservacao: form.estado_conservacao.trim(),
      ...(editing ? { ativo: form.ativo } : {}),
    })
  }

  return (
    <div className="modal-overlay patrimonio-modal-overlay" role="presentation" onMouseDown={event => event.target === event.currentTarget && !saving && onClose()}>
      <section ref={modalRef} className="modal patrimonio-form-modal" role="dialog" aria-modal="true" aria-labelledby="equipamento-modal-title">
        <form onSubmit={submit}>
          <div className="modal-header">
            <h2 id="equipamento-modal-title" className="modal-title">{editing ? 'Editar equipamento' : 'Cadastrar equipamento'}</h2>
            <button className="modal-close" type="button" onClick={onClose} disabled={saving} aria-label="Fechar">×</button>
          </div>

          <div className="modal-body patrimonio-modal-body form-stack">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="equipamento-patrimonio">Número do patrimônio</label>
                <input
                  id="equipamento-patrimonio"
                  name="numero_patrimonio"
                  data-autofocus
                  value={form.numero_patrimonio}
                  onChange={event => update({ numero_patrimonio: event.target.value })}
                  maxLength="80"
                  placeholder="Ex.: PAT-001"
                />
                <small className="form-hint">Único quando informado.</small>
              </div>
              <div className="form-group">
                <label htmlFor="equipamento-serie">Número de série</label>
                <input
                  id="equipamento-serie"
                  name="numero_serie"
                  value={form.numero_serie}
                  onChange={event => update({ numero_serie: event.target.value })}
                  maxLength="120"
                  placeholder="Número fornecido pelo fabricante"
                />
                <small className="form-hint">Único quando informado.</small>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="equipamento-tipo">Tipo</label>
                <select id="equipamento-tipo" name="tipo" value={form.tipo} onChange={event => update({ tipo: event.target.value })} required>
                  {TIPOS_EQUIPAMENTO.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="equipamento-marca">Marca</label>
                <input id="equipamento-marca" name="marca" value={form.marca} onChange={event => update({ marca: event.target.value })} maxLength="100" required />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="equipamento-modelo">Modelo</label>
              <input id="equipamento-modelo" name="modelo" value={form.modelo} onChange={event => update({ modelo: event.target.value })} maxLength="120" required />
            </div>

            <div className="form-group">
              <label htmlFor="equipamento-conservacao">Estado de conservação</label>
              <textarea
                id="equipamento-conservacao"
                name="estado_conservacao"
                value={form.estado_conservacao}
                onChange={event => update({ estado_conservacao: event.target.value })}
                rows="3"
                maxLength="300"
                placeholder="Descreva o estado atual do equipamento"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="equipamento-descricao">Descrição complementar</label>
              <textarea
                id="equipamento-descricao"
                name="descricao"
                value={form.descricao}
                onChange={event => update({ descricao: event.target.value })}
                rows="3"
                maxLength="2000"
                placeholder="Características ou observações relevantes (opcional)"
              />
            </div>

            {editing && equipamento.status !== 'baixado' && (
              <label className="patrimonio-checkbox">
                <input type="checkbox" checked={form.ativo} onChange={event => update({ ativo: event.target.checked })} />
                <span>
                  <strong>Equipamento ativo</strong>
                  <small>Itens inativos não ficam disponíveis para novos vínculos ou solicitações.</small>
                </span>
              </label>
            )}
          </div>

          <div className="modal-footer">
            <button className="btn btn-outline" type="button" onClick={onClose} disabled={saving}>Cancelar</button>
            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Salvando...' : editing ? 'Salvar alterações' : 'Cadastrar equipamento'}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
