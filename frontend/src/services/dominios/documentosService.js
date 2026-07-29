import { download, req, upload } from '../httpClient'
import { queryString } from '../../utils/queryString'

export const documentosService = {
  historicoDocumentos: (params = {}) => req('GET', `/documentos/historico${queryString(params)}`),
  uploadDocumento: formData => upload('/documentos/upload', formData),
  downloadDocumento: id => download(`/documentos/${id}/download`),
  excluirDocumento: id => req('DELETE', `/documentos/${id}`),
}
