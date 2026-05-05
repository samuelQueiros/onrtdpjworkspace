import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { EmptyState, LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

export default function MinhasFerias() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = () => api.minhasFerias().then(setItems).finally(() => setLoading(false))

  useEffect(() => {
    load()
  }, [])

  const cancel = async id => {
    if (!confirm('Cancelar este periodo de ferias?')) return
    setError('')
    try {
      await api.cancelarFerias(id)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) return <LoadingCard />

  return (
    <>
      <PageHeader
        title="Minhas Ferias"
        subtitle="Historico dos periodos registrados na sua conta."
        action={<Link className="btn btn-primary" to="/solicitar">Solicitar ferias</Link>}
      />
      {error && <div className="alert alert-error spaced">{error}</div>}
      <section className="card">
        <div className="table-wrap">
          {items.length ? (
            <table>
              <thead><tr><th>Inicio</th><th>Fim</th><th>Dias</th><th>Criado em</th><th>Status</th><th></th></tr></thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id}>
                    <td>{formatDate(item.data_inicio)}</td>
                    <td>{formatDate(item.data_fim)}</td>
                    <td>{item.dias_usados}</td>
                    <td>{formatDate(item.criado_em)}</td>
                    <td><StatusBadge tone="blue">Registrado</StatusBadge></td>
                    <td><button className="btn btn-danger btn-sm" onClick={() => cancel(item.id)}>Cancelar</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <EmptyState title="Sem ferias registradas" text="Solicite seu primeiro periodo para iniciar o controle." />}
        </div>
      </section>
    </>
  )
}
