import { useEffect, useState } from 'react'
import { api } from '../api'
import { LoadingCard, PageHeader, formatDate } from './_helpers'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

function exportRelatorios(colaboradores) {
  const resumoRows = [
    ['Tipo', 'Nome', 'Email', 'Dias totais', 'Dias usados', 'Dias restantes', 'Periodo inicio', 'Periodo fim', 'Dias do periodo'],
  ]

  colaboradores.forEach(colaborador => {
    resumoRows.push([
      'Resumo',
      colaborador.nome,
      colaborador.email,
      colaborador.dias_totais,
      colaborador.dias_usados,
      colaborador.dias_restantes,
      '',
      '',
      '',
    ])

    if (colaborador.ferias.length) {
      colaborador.ferias.forEach(ferias => {
        resumoRows.push([
          'Periodo',
          colaborador.nome,
          colaborador.email,
          '',
          '',
          '',
          formatDate(ferias.data_inicio),
          formatDate(ferias.data_fim),
          ferias.dias_usados,
        ])
      })
    }
  })

  const csv = `sep=;\r\n${resumoRows.map(row => row.map(csvCell).join(';')).join('\r\n')}`
  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `relatorio-ferias-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export default function Relatorios() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.relatorios().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingCard />

  const colaboradores = data?.colaboradores || []
  const totalDias = colaboradores.reduce((sum, item) => sum + item.dias_totais, 0)
  const usados = colaboradores.reduce((sum, item) => sum + item.dias_usados, 0)

  return (
    <>
      <PageHeader
        title="Relatorios"
        subtitle="Visao consolidada de uso de ferias por colaborador."
        action={<button className="btn btn-primary" onClick={() => exportRelatorios(colaboradores)} disabled={!colaboradores.length}>Exportar Excel</button>}
      />

      <section className="stat-grid">
        <div className="stat-card"><div className="stat-label">Colaboradores</div><div className="stat-value">{colaboradores.length}</div></div>
        <div className="stat-card"><div className="stat-label">Dias totais</div><div className="stat-value">{totalDias}</div></div>
        <div className="stat-card"><div className="stat-label">Dias usados</div><div className="stat-value">{usados}</div></div>
        <div className="stat-card"><div className="stat-label">Dias disponiveis</div><div className="stat-value">{totalDias - usados}</div></div>
      </section>

      <section className="card">
        <div className="card-header"><h2 className="card-title">Resumo por colaborador</h2></div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Nome</th><th>Email</th><th>Total</th><th>Usados</th><th>Restantes</th><th>Periodos</th></tr></thead>
            <tbody>
              {colaboradores.map(item => (
                <tr key={item.id}>
                  <td>{item.nome}</td>
                  <td>{item.email}</td>
                  <td>{item.dias_totais}</td>
                  <td>{item.dias_usados}</td>
                  <td>{item.dias_restantes}</td>
                  <td>{item.ferias.length ? item.ferias.map(f => `${formatDate(f.data_inicio)}-${formatDate(f.data_fim)}`).join(', ') : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}
