import { download, req, upload } from '../httpClient'

export const documentosService = {
  meusDocumentos: () => req('GET', '/documentos/me'),
  documentosUsuario: userId => req('GET', `/documentos/usuario/${userId}`),
  uploadDocumento: formData => upload('/documentos/upload', formData),
  downloadDocumento: id => download(`/documentos/${id}/download`),
  excluirDocumento: id => req('DELETE', `/documentos/${id}`),
}
