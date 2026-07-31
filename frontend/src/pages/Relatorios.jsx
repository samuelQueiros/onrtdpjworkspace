import { useEffect, useState } from 'react'
import '../styles/pages/relatorios.css'
import RelatorioResumoCards from '../components/relatorios/RelatorioResumoCards'
import RelatorioTabela from '../components/relatorios/RelatorioTabela'
import { api } from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { LoadingCard, PageHeader } from '../components/comum/PageHelpers'

export default function Relatorios() {
  const toast = useToast()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filtro, setFiltro] = useState('')
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    api.relatorios().then(setData).finally(() => setLoading(false))
  }, [])

  const exportar = async () => {
    setExporting(true)
    try {
      const blob = await api.exportarRelatorios()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `relatorio-ferias-${new Date().toISOString().slice(0, 10)}.xlsx`
      document.body.appendChild(link)
      link.click()
      link.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      toast.error(error.message)
    } finally {
      setExporting(false)
    }
  }

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
            onClick={exportar}
            disabled={!colaboradores.length || exporting}
          >
            {exporting ? 'Exportando...' : 'Exportar Excel'}
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
