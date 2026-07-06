import { formatDate } from './formatters'

function csvCell(value) {
  return `"${String(value ?? '').replace(/"/g, '""')}"`
}

export function exportRelatorios(colaboradores) {
  const rows = [
    ['Tipo', 'Nome', 'E-mail', 'Departamento', 'Dias totais', 'Dias usados', 'Dias restantes', 'Início período', 'Fim período', 'Dias do período'],
  ]

  colaboradores.forEach(colaborador => {
    rows.push([
      'Resumo',
      colaborador.nome,
      colaborador.email,
      colaborador.departamento?.nome || '',
      colaborador.dias_totais,
      colaborador.dias_usados,
      colaborador.dias_restantes,
      '',
      '',
      '',
    ])

    colaborador.ferias.forEach(ferias => {
      rows.push([
        'Período',
        colaborador.nome,
        colaborador.email,
        colaborador.departamento?.nome || '',
        '',
        '',
        '',
        formatDate(ferias.data_inicio),
        formatDate(ferias.data_fim),
        ferias.dias_usados,
      ])
    })
  })

  const csv = `sep=;\r\n${rows.map(row => row.map(csvCell).join(';')).join('\r\n')}`
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `relatorio-ferias-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
