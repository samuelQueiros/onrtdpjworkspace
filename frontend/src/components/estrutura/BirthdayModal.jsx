export default function BirthdayModal({ user, onClose }) {
  return (
    <div className="bday-overlay" onClick={onClose}>
      <div className="bday-card" onClick={event => event.stopPropagation()}>
        <div className="bday-emoji">🎂</div>
        <h2 className="bday-title">Feliz Aniversário!</h2>
        <p className="bday-msg">
          Parabéns, <strong>{user.nome.split(' ')[0]}</strong>!<br />
          A equipe do ONRTDPJ deseja a você um dia incrível e cheio de alegrias!
        </p>
        <button className="btn btn-primary bday-btn" onClick={onClose}>
          Obrigado! 🎉
        </button>
      </div>
    </div>
  )
}
