import { useEffect, useState } from 'react'
import { montarModeloEmailFerias } from '../../utils/emailTemplates'
import { useModalFocusTrap } from '../../utils/useModalFocusTrap'
import { api } from '../../services/api'

export default function EnviarLembreteFeriasModal({ alerta, onClose, onEnviado }) {
  const [destinatario, setDestinatario] = useState(null)
  const [carregandoConfig, setCarregandoConfig] = useState(true)
  const [erroConfig, setErroConfig] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [erroEnvio, setErroEnvio] = useState('')

  const fechar = () => { if (!enviando) onClose() }
  const modalRef = useModalFocusTrap(fechar)

  useEffect(() => {
    api.obterConfiguracao()
      .then(configuracao => setDestinatario(configuracao.email_destinatario))
      .catch(error => setErroConfig(error.message))
      .finally(() => setCarregandoConfig(false))
  }, [])

  const confirmar = async () => {
    setEnviando(true)
    setErroEnvio('')
    try {
      await api.enviarLembreteFerias(alerta.id)
      onEnviado()
    } catch (error) {
      setErroEnvio(error.message)
      setEnviando(false)
    }
  }

  const preview = montarModeloEmailFerias(alerta)

  return (
    <div className="modal-overlay" role="presentation" onMouseDown={fechar}>
      <section
        ref={modalRef}
        className="modal lembrete-ferias-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="enviar-lembrete-ferias-title"
        onMouseDown={event => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="ferias-alerta-kicker">Enviar aviso de férias por e-mail</p>
            <h3 id="enviar-lembrete-ferias-title">{alerta.ferias_usuario}</h3>
          </div>
          <button className="btn-close" type="button" onClick={fechar} disabled={enviando} aria-label="Fechar modal">×</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Destinatário</label>
            {carregandoConfig ? (
              <p className="muted">Carregando destinatário configurado...</p>
            ) : erroConfig ? (
              <div className="alert alert-error" role="alert">{erroConfig}</div>
            ) : (
              <input value={destinatario} readOnly disabled />
            )}
          </div>
          <div className="form-group">
            <label>Prévia do e-mail</label>
            <pre className="lembrete-ferias-preview">{preview}</pre>
          </div>
          {erroEnvio && <div className="alert alert-error" role="alert">{erroEnvio}</div>}
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" type="button" onClick={fechar} disabled={enviando}>Cancelar</button>
          <button
            data-autofocus
            className="btn btn-primary"
            type="button"
            onClick={confirmar}
            disabled={enviando || carregandoConfig || Boolean(erroConfig)}
          >
            {enviando ? 'Enviando...' : 'Confirmar envio'}
          </button>
        </div>
      </section>
    </div>
  )
}
