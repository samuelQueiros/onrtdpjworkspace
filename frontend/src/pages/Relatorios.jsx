import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { LoadingCard, PageHeader, StatusBadge, formatDate } from './_helpers'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

function exportRelatorios(colaboradores) {
  const rows = [
    ['Tipo', 'Nome', 'E-mail', 'Departamento', 'Dias totais', 'Dias usados', 'Dias restantes', 'Início período', 'Fim período', 'Dias do período'],
  ]

  colaboradores.forEach(col => {
    rows.push([
      'Resumo',
      col.nome,
      col.email,
      col.departamento?.nome || '',
      col.dias_totais,
      col.dias_usados,
      col.dias_restantes,
      '',
      '',
      '',
    ])

    col.ferias.forEach(f => {
      rows.push([
        'Período',
        col.nome,
        col.email,
        col.departamento?.nome || '',
        '',
        '',
        '',
        formatDate(f.data_inicio),
        formatDate(f.data_fim),
        f.dias_usados,
      ])
    })
  })

  const csv = `sep=;\r\n${rows.map(row => row.map(csvCell).join(';')).join('\r\n')}`
  const blob = new Blob([`﻿${csv}`], { type: 'text/csv;charset=utf-8;' })
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
  const [filtro, setFiltro] = useState('')

  useEffect(() => {
    api.relatorios().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingCard />

  const colaboradores = (data?.colaboradores || []).filter(c =>
    !filtro ||
    c.nome.toLowerCase().includes(filtro.toLowerCase()) ||
    (c.departamento?.nome || '').toLowerCase().includes(filtro.toLowerCase())
  )

  const totalDias = colaboradores.reduce((s, c) => s + c.dias_totais, 0)
  const usados = colaboradores.reduce((s, c) => s + c.dias_usados, 0)
  const pendentes = colaboradores.reduce((s, c) => s + c.ferias_pendentes.length, 0)

  return (
    <>
      <PageHeader
        title="Relatórios"
        subtitle="Visão consolidada de uso de férias por colaborador."
        action={
          <button
            className="btn btn-primary"
            onClick={() => exportRelatorios(data?.colaboradores || [])}
            disabled={!colaboradores.length}
          >
            Exportar Excel
          </button>
        }
      />

      <section className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Colaboradores</div>
          <div className="stat-value">{data?.colaboradores?.length ?? 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias totais</div>
          <div className="stat-value">{totalDias}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dias usados</div>
          <div className="stat-value">{usados}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pendentes</div>
          <div className="stat-value">{pendentes}</div>
          <div className="stat-sub">aguardando aprovação</div>
        </div>
      </section>

      <section className="card">
        <div className="card-header">
          <h2 className="card-title">Resumo por colaborador</h2>
          <input
            className="search-input"
            placeholder="Filtrar por nome ou departamento..."
            value={filtro}
            onChange={e => setFiltro(e.target.value)}
          />
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Departamento</th>
                <th>Total</th>
                <th>Usados</th>
                <th>Restantes</th>
                <th>Pendentes</th>
                <th>Períodos</th>
              </tr>
            </thead>
            <tbody>
              {colaboradores.map(item => (
                <tr key={item.id}>
                  <td>{item.nome}</td>
                  <td>{item.email}</td>
                  <td>{item.departamento?.nome || <span className="muted">—</span>}</td>
                  <td>{item.dias_totais}</td>
                  <td>{item.dias_usados}</td>
                  <td>
                    <StatusBadge tone={item.dias_restantes > 10 ? 'green' : item.dias_restantes > 0 ? 'amber' : 'red'}>
                      {item.dias_restantes}
                    </StatusBadge>
                  </td>
                  <td>
                    {item.ferias_pendentes.length > 0
                      ? <StatusBadge tone="amber">{item.ferias_pendentes.length}</StatusBadge>
                      : <span className="muted">—</span>}
                  </td>
                  <td>
                    {item.ferias.length
                      ? item.ferias.map(f => `${formatDate(f.data_inicio)}–${formatDate(f.data_fim)}`).join(', ')
                      : <span className="muted">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  )
}
