import { useEffect, useRef } from 'react'

const FOCUSABLE = 'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])'

export function useModalFocusTrap(onClose) {
  const modalRef = useRef(null)
  const closeRef = useRef(onClose)
  closeRef.current = onClose

  useEffect(() => {
    const previousFocus = document.activeElement
    const focusable = [...(modalRef.current?.querySelectorAll(FOCUSABLE) || [])]
    const initialFocus = modalRef.current?.querySelector('[data-autofocus]') || focusable[0]
    initialFocus?.focus()
    const onKeyDown = event => {
      if (event.key === 'Escape') closeRef.current()
      const currentFocusable = [...(modalRef.current?.querySelectorAll(FOCUSABLE) || [])]
      if (event.key !== 'Tab' || !currentFocusable.length) return
      const first = currentFocusable[0]
      const last = currentFocusable[currentFocusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus()
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      previousFocus?.focus?.()
    }
  }, [])

  return modalRef
}
