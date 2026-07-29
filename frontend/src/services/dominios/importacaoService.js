import { download, upload } from '../httpClient'

export const importacaoService = {
  baixarModeloColaboradores: () => download('/importacao/colaboradores/modelo'),
  importarColaboradores: formData => upload('/importacao/colaboradores', formData),
  importarLogs: formData => upload('/importacao/logs', formData),
}
