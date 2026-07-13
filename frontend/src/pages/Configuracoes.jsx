import { useEffect, useState } from 'react'
import '../styles/pages/configuracoes.css'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'
import { useConfirm } from '../contexts/ConfirmContext'
import { useToast } from '../contexts/ToastContext'
import { api } from '../services/api'

export default function Configuracoes() {
  const confirmar = useConfirm()
  const toast = useToast()
  const [cargos, setCargos] = useState([])
  const [nome, setNome] = useState('')
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => api.listarCargos()
    .then(setCargos)
    .catch(error => toast.error(error.message))
    .finally(() => setLoading(false))
  useEffect(() => { load() }, [])

  const reset = () => { setNome(''); setEditing(null) }

  const save = async event => {
    event.preventDefault()
    try {
      if (editing) {
        await api.editarCargo(editing, { nome })
        toast.success('Cargo atualizado.')
      } else {
        await api.criarCargo({ nome })
        toast.success('Cargo criado.')
      }
      reset()
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

  const startEdit = cargo => { setEditing(cargo.id); setNome(cargo.nome) }

  const excluir = async cargo => {
    const confirmado = await confirmar({
      title: 'Excluir cargo?',
      message: cargo.total_usuarios
        ? `${cargo.total_usuarios} colaborador(es) ficarão sem cargo. Esta ação não pode ser desfeita.`
        : 'Esta ação não pode ser desfeita.',
      confirmLabel: 'Excluir cargo',
    })
    if (!confirmado) return
    try {
      await api.excluirCargo(cargo.id)
      if (editing === cargo.id) reset()
      toast.success('Cargo excluído.')
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader title="Configurações" subtitle="Gerencie as opções utilizadas nos cadastros do sistema." />
      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <div className="card-header"><h2 className="card-title">Cargos cadastrados</h2></div>
          <div className="table-wrap">
            {cargos.length ? (
              <table>
                <thead><tr><th>Nome</th><th>Colaboradores</th><th></th></tr></thead>
                <tbody>
                  {cargos.map(cargo => (
                    <tr key={cargo.id}>
                      <td><strong>{cargo.nome}</strong></td>
                      <td>{cargo.total_usuarios}</td>
                      <td className="actions-cell">
                        <button className="btn btn-outline btn-sm" onClick={() => startEdit(cargo)}>Editar</button>
                        <button className="btn btn-danger btn-sm" onClick={() => excluir(cargo)}>Excluir</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : <div className="empty"><p>Nenhum cargo cadastrado.</p></div>}
          </div>
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header"><h2 className="card-title">{editing ? 'Editar cargo' : 'Novo cargo'}</h2></div>
          <div className="card-body form-stack">
            <div className="form-group">
              <label>Nome do cargo</label>
              <input value={nome} onChange={event => setNome(event.target.value)} maxLength="100" required />
            </div>
            <div className="button-row">
              {editing && <button className="btn btn-outline" type="button" onClick={reset}>Cancelar</button>}
              <button className="btn btn-primary" type="submit">{editing ? 'Salvar alterações' : 'Criar cargo'}</button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}
