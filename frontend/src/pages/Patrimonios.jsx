import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/patrimonios.css'
import AcaoPatrimonioModal from '../components/patrimonios/AcaoPatrimonioModal'
import DetalhesPatrimonioModal from '../components/patrimonios/DetalhesPatrimonioModal'
import EquipamentoModal from '../components/patrimonios/EquipamentoModal'
import FiltrosPatrimonios, { blankPatrimonioFilters } from '../components/patrimonios/FiltrosPatrimonios'
import PatrimoniosTabela from '../components/patrimonios/PatrimoniosTabela'
import { PageHeader } from '../components/comum/PageHelpers'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { patrimoniosService } from '../services/dominios/patrimoniosService'
import { usersService } from '../services/dominios/usersService'

const blankPage = { items: [], total: 0, page: 1, page_size: 25, pages: 1 }

const ACTION_SUCCESS = {
  vincular: 'Equipamento vinculado com sucesso.',
  desvincular: 'Vínculo encerrado e preservado no histórico.',
  manutencao: 'Manutenção registrada.',
  finalizar_manutencao: 'Manutenção finalizada. O equipamento está disponível novamente.',
  baixa: 'Baixa registrada. O histórico do equipamento foi preservado.',
}

export default function Patrimonios() {
  const toast = useToast()
  const confirmar = useConfirm()
  const [data, setData] = useState(blankPage)
  const [users, setUsers] = useState([])
  const [filters, setFilters] = useState(blankPatrimonioFilters)
  const [appliedFilters, setAppliedFilters] = useState(blankPatrimonioFilters)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [detailLoadingId, setDetailLoadingId] = useState(null)
  const [equipmentModal, setEquipmentModal] = useState(null)
  const [details, setDetails] = useState(null)
  const [actionModal, setActionModal] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = useCallback(async (page = 1, selectedFilters = blankPatrimonioFilters, initial = false) => {
    if (initial) setLoading(true)
    else setRefreshing(true)
    try {
      const response = await patrimoniosService.listarEquipamentos({
        ...selectedFilters,
        page,
        page_size: 25,
      })
      setData(response)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [toast])

  useEffect(() => {
    load(1, blankPatrimonioFilters, true)
    usersService.listarUsuarios()
      .then(setUsers)
      .catch(error => toast.error(`Não foi possível carregar os colaboradores: ${error.message}`))
  }, [load, toast])

  const applyFilters = event => {
    event.preventDefault()
    const next = { ...filters }
    setAppliedFilters(next)
    load(1, next)
  }

  const clearFilters = () => {
    const cleared = { ...blankPatrimonioFilters }
    setFilters(cleared)
    setAppliedFilters(cleared)
    load(1, cleared)
  }

  const changePage = page => load(page, appliedFilters)

  const openDetails = async equipamento => {
    setDetailLoadingId(equipamento.id)
    try {
      setDetails(await patrimoniosService.obterEquipamento(equipamento.id))
    } catch (error) {
      toast.error(error.message)
    } finally {
      setDetailLoadingId(null)
    }
  }

  const openCreate = () => setEquipmentModal({ equipamento: null })
  const openEdit = equipamento => {
    setDetails(null)
    setEquipmentModal({ equipamento })
  }

  const saveEquipment = async payload => {
    const editing = equipmentModal?.equipamento
    if (editing?.ativo && payload.ativo === false) {
      const confirmed = await confirmar({
        title: 'Desativar equipamento?',
        message: 'O item deixará de ficar disponível para vínculos e solicitações. Seu histórico será preservado.',
        confirmLabel: 'Desativar equipamento',
      })
      if (!confirmed) return
    }

    setSaving(true)
    try {
      if (editing) {
        await patrimoniosService.editarEquipamento(editing.id, payload)
        toast.success('Equipamento atualizado com sucesso.')
      } else {
        await patrimoniosService.criarEquipamento(payload)
        toast.success('Equipamento cadastrado com sucesso.')
      }
      setEquipmentModal(null)
      await load(editing ? data.page : 1, appliedFilters)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  const openAction = action => {
    setActionModal({ action, equipamento: details })
    setDetails(null)
  }

  const saveAction = async payload => {
    const { action, equipamento } = actionModal
    const handlers = {
      vincular: patrimoniosService.vincularEquipamento,
      desvincular: patrimoniosService.desvincularEquipamento,
      manutencao: patrimoniosService.registrarManutencao,
      finalizar_manutencao: patrimoniosService.finalizarManutencao,
      baixa: patrimoniosService.baixarEquipamento,
    }

    setSaving(true)
    try {
      await handlers[action](equipamento.id, payload)
      toast.success(ACTION_SUCCESS[action])
      setActionModal(null)
      await load(data.page, appliedFilters)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <PageHeader
        title="Patrimônios"
        subtitle="Cadastre equipamentos, acompanhe responsáveis e preserve todo o histórico de movimentações."
        action={<button className="btn btn-primary" type="button" onClick={openCreate}>+ Cadastrar equipamento</button>}
      />

      <div className="patrimonios-page-stack">
        <FiltrosPatrimonios
          filters={filters}
          users={users}
          onChange={setFilters}
          onClear={clearFilters}
          onSubmit={applyFilters}
          busy={refreshing}
        />

        <PatrimoniosTabela
          data={data}
          loading={loading || refreshing}
          detailLoadingId={detailLoadingId}
          onDetails={openDetails}
          onEdit={openEdit}
          onPageChange={changePage}
        />
      </div>

      {equipmentModal && (
        <EquipamentoModal
          equipamento={equipmentModal.equipamento}
          saving={saving}
          onClose={() => !saving && setEquipmentModal(null)}
          onSave={saveEquipment}
        />
      )}

      {details && (
        <DetalhesPatrimonioModal
          equipamento={details}
          onAction={openAction}
          onClose={() => setDetails(null)}
          onEdit={() => openEdit(details)}
        />
      )}

      {actionModal && (
        <AcaoPatrimonioModal
          action={actionModal.action}
          equipamento={actionModal.equipamento}
          users={users}
          saving={saving}
          onClose={() => !saving && setActionModal(null)}
          onSave={saveAction}
        />
      )}
    </>
  )
}
