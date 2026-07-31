import { useModalFocusTrap } from '../../utils/useModalFocusTrap'

export default function BirthdayModal({ user, onClose }) {
  const modalRef = useModalFocusTrap(onClose)

  return (
    <div className="bday-overlay" role="presentation" onClick={onClose}>
      <div
        ref={modalRef}
        className="bday-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="birthday-modal-title"
        onClick={event => event.stopPropagation()}
      >
        <div className="bday-emoji">🎂</div>
        <h2 id="birthday-modal-title" className="bday-title">Feliz Aniversário!</h2>
        <p className="bday-msg">
          Parabéns, <strong>{user.nome.split(' ')[0]}</strong>!<br />
          A equipe do ONRTDPJ deseja a você um dia incrível e cheio de alegrias!
        </p>
        <button type="button" data-autofocus className="btn btn-primary bday-btn" onClick={onClose}>
          Obrigado! 🎉
        </button>
      </div>
    </div>
  )
}
