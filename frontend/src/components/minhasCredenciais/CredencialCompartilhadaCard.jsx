import { useState } from 'react'

export default function CredencialCompartilhadaCard({
  copiado,
  credencial,
  onCopiar,
  onOcultar,
  onRevelar,
  revelando,
  segredo,
}) {
  const [senhaAtual, setSenhaAtual] = useState('')

  const revelar = async () => {
    const revelado = await onRevelar(credencial.id, senhaAtual)
    if (revelado) setSenhaAtual('')
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">{credencial.descricao}</h2>
      </div>
      <div className="card-body stack-12">
        <div className="inline-center gap-8">
          <span className="credential-field-label">E-mail</span>
          <span className="flex-1">{credencial.email}</span>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onCopiar(`email-${credencial.id}`, credencial.email)}
          >
            {copiado[`email-${credencial.id}`] ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        <div className="inline-center gap-8">
          <span className="credential-field-label">Senha</span>
          <span className={`credential-secret${segredo ? '' : ' masked'}`}>
            {segredo || '********'}
          </span>
          {segredo ? (
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={() => onOcultar(credencial.id)}
            >
              Ocultar
            </button>
          ) : null}
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => onCopiar(`senha-${credencial.id}`, segredo)}
            disabled={!segredo}
          >
            {copiado[`senha-${credencial.id}`] ? 'Copiado!' : 'Copiar'}
          </button>
        </div>
        {!segredo ? (
          <div className="inline-center gap-8">
            <label className="credential-field-label" htmlFor={`senha-atual-${credencial.id}`}>
              Sua senha
            </label>
            <input
              id={`senha-atual-${credencial.id}`}
              type="password"
              autoComplete="current-password"
              value={senhaAtual}
              onChange={event => setSenhaAtual(event.target.value)}
              disabled={revelando}
              required
            />
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={revelar}
              disabled={revelando || !senhaAtual}
            >
              {revelando ? 'Validando...' : 'Revelar'}
            </button>
          </div>
        ) : null}
      </div>
    </div>
  )
}
