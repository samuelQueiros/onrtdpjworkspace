import { download, req } from '../httpClient'

export const relatoriosService = {
  relatorios: () => req('GET', '/relatorios'),
  exportarRelatorios: () => download('/relatorios/exportar'),
  dashboard: () => req('GET', '/dashboard'),
  logs: (page = 1, pageSize = 50) => req('GET', `/logs?page=${page}&page_size=${pageSize}`),
  exportarLogs: () => download('/logs/exportar'),
}
