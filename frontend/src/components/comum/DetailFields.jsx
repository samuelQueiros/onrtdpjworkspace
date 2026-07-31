export function DetailField({ label, children, wide = false }) {
  const vazio = children === null || children === undefined || children === ''

  return (
    <div className={`user-detail-field${wide ? ' user-detail-field-wide' : ''}`}>
      <span>{label}</span>
      <strong className={vazio ? 'muted' : undefined}>{vazio ? 'Não informado' : children}</strong>
    </div>
  )
}

export function EditableField({ label, wide = false, editing, edit, children }) {
  if (editing) {
    return (
      <div className={`user-detail-field${wide ? ' user-detail-field-wide' : ''}`}>
        <span>{label}</span>
        {edit}
      </div>
    )
  }
  return <DetailField label={label} wide={wide}>{children}</DetailField>
}

export function DetailSection({ title, children }) {
  return (
    <section>
      <h3 className="user-detail-section-title">{title}</h3>
      <div className="user-details-grid">{children}</div>
    </section>
  )
}
