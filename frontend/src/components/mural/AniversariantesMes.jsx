import { formatDate } from '../../utils/formatters'
import BirthdayAvatar from './BirthdayAvatar'

export default function AniversariantesMes({ aniversariantes }) {
  if (!aniversariantes.length) return null

  return (
    <section className="card spaced">
      <div className="card-header">
        <h2 className="card-title">Aniversariantes do mês</h2>
      </div>
      <div className="card-body">
        <div className="birthday-grid">
          {aniversariantes.map((item, index) => (
            <div key={index} className="birthday-card">
              <BirthdayAvatar nome={item.nome} />
              <strong className="birthday-nome">{item.nome}</strong>
              <span className="birthday-data">🎂 {formatDate(item.data_aniversario)}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
