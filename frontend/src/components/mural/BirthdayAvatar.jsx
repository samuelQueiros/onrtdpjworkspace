import { avatarColor, getInitials } from './avatarMural'

export default function BirthdayAvatar({ nome }) {
  return (
    <div className="birthday-avatar" style={{ background: avatarColor(nome) }}>
      {getInitials(nome)}
    </div>
  )
}
