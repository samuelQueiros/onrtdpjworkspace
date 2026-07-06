import { useEffect, useState } from 'react'
import RelatorioResumoCards from '../components/relatorios/RelatorioResumoCards'
import RelatorioTabela from '../components/relatorios/RelatorioTabela'
import { api } from '../services/api'
import { exportRelatorios } from '../utils/relatoriosExport'
import { LoadingCard, PageHeader } from './_helpers'

export default function Relatorios() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState('')

  useEffect(() => {
    api.relatorios().then(setData).finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingCard />

  const colaboradores = (data?.colaboradores || []).filter(colaborador =>
    !filtro ||
    colaborador.nome.toLowerCase().includes(filtro.toLowerCase()) ||
    (colaborador.departamento?.nome || '').toLowerCase().includes(filtro.toLowerCase())
  )

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

      <RelatorioResumoCards colaboradores={colaboradores} totalColaboradores={data?.colaboradores?.length ?? 0} />

      <RelatorioTabela
        colaboradores={colaboradores}
        filtro={filtro}
        onFiltroChange={setFiltro}
      />
    </>
  )
}
