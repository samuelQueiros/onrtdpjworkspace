import { useCallback, useEffect, useState } from 'react'
import '../styles/pages/configuracoes.css'
import { LoadingCard, PageHeader, StatusBadge } from '../components/comum/PageHelpers'
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
  const [cargosOpen, setCargosOpen] = useState(false)
  const [departamentos, setDepartamentos] = useState([])
  const [departamentosOpen, setDepartamentosOpen] = useState(false)
  const [departamentoForm, setDepartamentoForm] = useState({ nome: '', limite_simultaneo: 2 })
  const [departamentoEditing, setDepartamentoEditing] = useState(null)

  const load = useCallback(() => Promise.all([api.listarCargos(), api.listarDepartamentos()])
    .then(([listaCargos, listaDepartamentos]) => {
      setCargos(listaCargos)
      setDepartamentos(listaDepartamentos)
    })
    .catch(error => toast.error(error.message))
    .finally(() => setLoading(false)), [toast])
  useEffect(() => { load() }, [load])

  const reset = () => { setNome(''); setEditing(null) }
  const resetDepartamento = () => {
    setDepartamentoForm({ nome: '', limite_simultaneo: 2 })
    setDepartamentoEditing(null)
  }

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

  const saveDepartamento = async event => {
    event.preventDefault()
    const payload = { nome: departamentoForm.nome, limite_simultaneo: Number(departamentoForm.limite_simultaneo) }
    try {
      if (departamentoEditing) {
        await api.editarDepartamento(departamentoEditing, payload)
        toast.success('Departamento atualizado.')
      } else {
        await api.criarDepartamento(payload)
        toast.success('Departamento criado.')
      }
      resetDepartamento()
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

  const startEditDepartamento = departamento => {
    setDepartamentoEditing(departamento.id)
    setDepartamentoForm({ nome: departamento.nome, limite_simultaneo: departamento.limite_simultaneo })
  }

  const excluirDepartamento = async departamento => {
    const confirmado = await confirmar({
      title: 'Excluir departamento?',
      message: departamento.total_usuarios
        ? `${departamento.total_usuarios} colaborador(es) ficarão sem departamento. Esta ação não pode ser desfeita.`
        : 'Esta ação não pode ser desfeita.',
      confirmLabel: 'Excluir departamento',
    })
    if (!confirmado) return
    try {
      await api.excluirDepartamento(departamento.id)
      if (departamentoEditing === departamento.id) resetDepartamento()
      toast.success('Departamento excluído.')
      await load()
    } catch (error) {
      toast.error(error.message)
    }
  }

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
      <div className="settings-groups">
      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <button
            className="card-header disclosure-button disclosure-button-card"
            type="button"
            aria-expanded={cargosOpen}
            aria-controls="lista-cargos"
            onClick={() => setCargosOpen(open => !open)}
          >
            <span className="card-title">Cargos cadastrados <span className="muted">({cargos.length})</span></span>
            <span className="disclosure-chevron" aria-hidden="true">{cargosOpen ? '−' : '+'}</span>
          </button>
          {cargosOpen && <div id="lista-cargos" className="table-wrap">
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
          </div>}
        </section>

        <form className="card form-card" onSubmit={save}>
          <div className="card-header"><h2 className="card-title">{editing ? 'Editar cargo' : 'Novo cargo'}</h2></div>
          <div className="card-body form-stack">
            <div className="form-group">
              <label htmlFor="cargo-nome">Nome do cargo</label>
              <input id="cargo-nome" name="nome" value={nome} onChange={event => setNome(event.target.value)} maxLength="100" required />
            </div>
            <div className="button-row">
              {editing && <button className="btn btn-outline" type="button" onClick={reset}>Cancelar</button>}
              <button className="btn btn-primary" type="submit">{editing ? 'Salvar alterações' : 'Criar cargo'}</button>
            </div>
          </div>
        </form>
      </div>

      <div className="grid-2 grid-2-wide-left">
        <section className="card">
          <button className="card-header disclosure-button disclosure-button-card" type="button" aria-expanded={departamentosOpen} aria-controls="lista-departamentos" onClick={() => setDepartamentosOpen(open => !open)}>
            <span className="card-title">Departamentos cadastrados <span className="muted">({departamentos.length})</span></span>
            <span className="disclosure-chevron" aria-hidden="true">{departamentosOpen ? '−' : '+'}</span>
          </button>
          {departamentosOpen && <div id="lista-departamentos" className="table-wrap">
            {departamentos.length ? (
              <table>
                <thead><tr><th>Nome</th><th>Limite simultâneo</th><th>Colaboradores</th><th></th></tr></thead>
                <tbody>{departamentos.map(departamento => (
                  <tr key={departamento.id}>
                    <td><strong>{departamento.nome}</strong></td>
                    <td><StatusBadge tone="navy">{departamento.limite_simultaneo} simultâneo(s)</StatusBadge></td>
                    <td>{departamento.total_usuarios}</td>
                    <td className="actions-cell">
                      <button className="btn btn-outline btn-sm" onClick={() => startEditDepartamento(departamento)}>Editar</button>
                      <button className="btn btn-danger btn-sm" onClick={() => excluirDepartamento(departamento)}>Excluir</button>
                    </td>
                  </tr>
                ))}</tbody>
              </table>
            ) : <div className="empty"><p>Nenhum departamento cadastrado.</p></div>}
          </div>}
        </section>

        <form className="card form-card" onSubmit={saveDepartamento}>
          <div className="card-header"><h2 className="card-title">{departamentoEditing ? 'Editar departamento' : 'Novo departamento'}</h2></div>
          <div className="card-body form-stack">
            <div className="form-group">
              <label htmlFor="departamento-nome">Nome do setor</label>
              <input id="departamento-nome" name="nome" value={departamentoForm.nome} onChange={event => setDepartamentoForm({ ...departamentoForm, nome: event.target.value })} maxLength="100" required />
            </div>
            <div className="form-group">
              <label htmlFor="departamento-limite">Limite de férias simultâneas</label>
              <input id="departamento-limite" name="limite_simultaneo" type="number" min="1" max="50" value={departamentoForm.limite_simultaneo} onChange={event => setDepartamentoForm({ ...departamentoForm, limite_simultaneo: event.target.value })} required />
              <small className="form-hint">Máximo de colaboradores do setor em férias ao mesmo tempo.</small>
            </div>
            <div className="button-row">
              {departamentoEditing && <button className="btn btn-outline" type="button" onClick={resetDepartamento}>Cancelar</button>}
              <button className="btn btn-primary" type="submit">{departamentoEditing ? 'Salvar alterações' : 'Criar departamento'}</button>
            </div>
          </div>
        </form>
      </div>
      </div>
    </>
  )
}
