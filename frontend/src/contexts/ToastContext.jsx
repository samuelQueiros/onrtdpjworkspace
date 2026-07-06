import { createContext, useCallback, useContext, useMemo, useState } from 'react'

const ToastContext = createContext(null)

const DEFAULT_DURATION = 4500

function Toast({ toast, onClose }) {
  const title = toast.title || (toast.type === 'success' ? 'Sucesso' : 'Erro')

  return (
    <div
      className={`toast toast-${toast.type}`}
      role={toast.type === 'error' ? 'alert' : 'status'}
      aria-live={toast.type === 'error' ? 'assertive' : 'polite'}
    >
      <div className="toast-content">
        <strong>{title}</strong>
        <span>{toast.message}</span>
      </div>
      <button
        type="button"
        className="toast-close"
        onClick={() => onClose(toast.id)}
        aria-label="Fechar notificação"
      >
        x
      </button>
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const remove = useCallback(id => {
    setToasts(current => current.filter(toast => toast.id !== id))
  }, [])

  const show = useCallback((type, message, options = {}) => {
    if (!message) return

    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`
    const toast = { id, type, message, title: options.title }

    setToasts(current => [...current, toast])
    window.setTimeout(() => remove(id), options.duration || DEFAULT_DURATION)
  }, [remove])

  const value = useMemo(() => ({
    success: (message, options) => show('success', message, options),
    error: (message, options) => show('error', message, options),
  }), [show])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="toast-viewport">
        {toasts.map(toast => (
          <Toast key={toast.id} toast={toast} onClose={remove} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast deve ser usado dentro de ToastProvider')
  return context
}
