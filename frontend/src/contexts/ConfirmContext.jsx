import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'

const ConfirmContext = createContext(null)

const DEFAULT_OPTIONS = {
  title: 'Confirmar ação',
  message: 'Deseja continuar?',
  confirmLabel: 'Confirmar',
  cancelLabel: 'Cancelar',
  tone: 'danger',
}

export function ConfirmProvider({ children }) {
  const [dialog, setDialog] = useState(null)
  const previousFocus = useRef(null)
  const dialogRef = useRef(null)

  const close = useCallback(result => {
    setDialog(current => {
      if (current?.resolve) current.resolve(result)
      return null
    })
    window.setTimeout(() => previousFocus.current?.focus?.(), 0)
  }, [])

  const confirmar = useCallback(options =>
    new Promise(resolve => {
      previousFocus.current = document.activeElement
      setDialog({ ...DEFAULT_OPTIONS, ...options, resolve })
    }), [])

  useEffect(() => {
    if (!dialog) return undefined
    const onKeyDown = event => {
      if (event.key === 'Escape') close(false)
      if (event.key === 'Tab' && dialogRef.current) {
        const focusable = [...dialogRef.current.querySelectorAll(
          'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
        )]
        if (!focusable.length) return
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault()
          first.focus()
        }
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [dialog, close])

  const value = useMemo(() => ({ confirmar }), [confirmar])

  return (
    <ConfirmContext.Provider value={value}>
      {children}
      {dialog && (
        <div className="confirm-overlay" role="presentation" onClick={() => close(false)}>
          <section
            ref={dialogRef}
            className="confirm-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
            aria-describedby="confirm-message"
            onClick={event => event.stopPropagation()}
          >
            <header className="confirm-header">
              <div>
                <p className={`confirm-kicker confirm-kicker-${dialog.tone}`}>
                  {dialog.tone === 'danger' ? 'Ação destrutiva' : 'Confirmação'}
                </p>
                <h2 id="confirm-title">{dialog.title}</h2>
              </div>
              <button
                type="button"
                className="btn-close"
                onClick={() => close(false)}
                aria-label="Fechar confirmação"
              >
                x
              </button>
            </header>
            <p id="confirm-message" className="confirm-message">
              {dialog.message}
            </p>
            <footer className="confirm-footer">
              <button type="button" className="btn btn-outline" onClick={() => close(false)} autoFocus>
                {dialog.cancelLabel}
              </button>
              <button
                type="button"
                className={dialog.tone === 'danger' ? 'btn btn-danger' : 'btn btn-primary'}
                onClick={() => close(true)}
              >
                {dialog.confirmLabel}
              </button>
            </footer>
          </section>
        </div>
      )}
    </ConfirmContext.Provider>
  )
}

export function useConfirm() {
  const context = useContext(ConfirmContext)
  if (!context) throw new Error('useConfirm deve ser usado dentro de ConfirmProvider')
  return context.confirmar
}
