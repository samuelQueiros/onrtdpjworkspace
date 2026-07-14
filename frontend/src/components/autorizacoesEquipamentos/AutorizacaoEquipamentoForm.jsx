import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { useToast } from '../../contexts/ToastContext'
import EquipamentoSelecionavel from './EquipamentoSelecionavel'
import { EmptyState } from '../comum/PageHelpers'

export default function AutorizacaoEquipamentoForm() {
  const navigate = useNavigate()
  const toast = useToast()
  const [tipo, setTipo] = useState('itens_vinculados')
  const [vinculados, setVinculados] = useState([])
  const [disponiveis, setDisponiveis] = useState([])
  const [selecionados, setSelecionados] = useState([])
  const [observacoes, setObservacoes] = useState('')
  const [loading, setLoading] = useState(true)
  const [loadingDisponiveis, setLoadingDisponiveis] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api.meusPatrimonios()
      .then(items => {
        setVinculados(items)
        setSelecionados(items.map(item => item.id))
      })
      .catch(error => toast.error(error.message))
      .finally(() => setLoading(false))
  }, [])

  const mudarTipo = novoTipo => {
    setTipo(novoTipo)
    if (novoTipo === 'itens_vinculados') {
      setSelecionados(vinculados.map(item => item.id))
      return
    }
    setSelecionados([])
    if (!disponiveis.length) {
      setLoadingDisponiveis(true)
      api.patrimoniosDisponiveis()
        .then(setDisponiveis)
        .catch(error => toast.error(error.message))
        .finally(() => setLoadingDisponiveis(false))
    }
  }

  const alternar = id => setSelecionados(atual => (
    atual.includes(id) ? atual.filter(item => item !== id) : [...atual, id]
  ))

  const enviar = async event => {
    event.preventDefault()
    if (!selecionados.length) return toast.error('Selecione pelo menos um equipamento.')
    setSaving(true)
    try {
      await api.criarAutorizacaoEquipamento({
        tipo_solicitacao: tipo,
        equipamento_ids: selecionados,
        observacoes: observacoes.trim() || null,
      })
      toast.success('Solicitação de equipamento enviada para aprovação.')
      window.dispatchEvent(new Event('approvals:changed'))
      navigate('/minhas-autorizacoes')
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const lista = tipo === 'itens_vinculados' ? vinculados : disponiveis

  return (
    <form className="equipment-request-form" onSubmit={enviar}>
      <div className="alert alert-info">
        Aprovação, entrega e aceite são etapas distintas. As datas oficiais serão registradas pelo sistema.
      </div>

      <fieldset className="request-type-options">
        <legend>Quais equipamentos deseja levar?</legend>
        <label>
          <input
            type="radio"
            name="tipo_solicitacao_equipamento"
            checked={tipo === 'itens_vinculados'}
            onChange={() => mudarTipo('itens_vinculados')}
          />
          Itens atualmente vinculados a mim
        </label>
        <label>
          <input
            type="radio"
            name="tipo_solicitacao_equipamento"
            checked={tipo === 'item_diferente'}
            onChange={() => mudarTipo('item_diferente')}
          />
          Solicitar um equipamento diferente
        </label>
      </fieldset>

      <fieldset className="equipment-options" disabled={loading || loadingDisponiveis}>
        <legend>Selecione os itens</legend>
        {(loading || loadingDisponiveis) ? (
          <div className="request-inline-loading"><div className="spinner" /> Carregando equipamentos...</div>
        ) : lista.length ? (
          lista.map(equipamento => (
            <EquipamentoSelecionavel
              key={equipamento.id}
              equipamento={equipamento}
              checked={selecionados.includes(equipamento.id)}
              onChange={alternar}
            />
          ))
        ) : (
          <EmptyState
            title={tipo === 'itens_vinculados' ? 'Nenhum item vinculado' : 'Nenhum equipamento disponível'}
            text={tipo === 'itens_vinculados'
              ? 'Peça ao administrador para conferir seus vínculos de patrimônio.'
              : 'Somente equipamentos ativos e realmente disponíveis são exibidos.'}
          />
        )}
      </fieldset>

      <div className="form-group">
        <label htmlFor="autorizacao-equipamento-observacoes">Observações (opcional)</label>
        <textarea
          id="autorizacao-equipamento-observacoes"
          value={observacoes}
          onChange={event => setObservacoes(event.target.value)}
          maxLength="2000"
          rows="3"
          placeholder="Informe alguma necessidade relevante para a análise."
        />
      </div>

      <div className="request-form-footer">
        <span aria-live="polite">{selecionados.length} item(ns) selecionado(s)</span>
        <button className="btn btn-primary" type="submit" disabled={saving || loading || !selecionados.length}>
          {saving ? 'Enviando...' : 'Enviar solicitação'}
        </button>
      </div>
    </form>
  )
}
