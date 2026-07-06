import { upload } from '../httpClient'

export const importacaoService = {
  importarFerias: formData => upload('/importacao/ferias', formData),
  importarLogs: formData => upload('/importacao/logs', formData),
}
