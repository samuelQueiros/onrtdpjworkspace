import { useModalFocusTrap } from '../../utils/useModalFocusTrap'

export default function ModalAutorizacaoBase({ busy = false, children, className = '', onClose, subtitle, title, titleId }) {
  const close = () => { if (!busy) onClose() }
  const modalRef = useModalFocusTrap(close)

  return (
    <div className="modal-overlay autorizacao-modal-overlay" role="presentation" onMouseDown={close}>
      <section
        ref={modalRef}
        className={`modal autorizacao-modal ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onMouseDown={event => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            {subtitle && <p className="autorizacao-modal-kicker">{subtitle}</p>}
            <h3 id={titleId}>{title}</h3>
          </div>
          <button className="btn-close" type="button" onClick={close} disabled={busy} aria-label="Fechar modal">×</button>
        </div>
        {children}
      </section>
    </div>
  )
}
