export default function UserDot({ cor, nome }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: 10,
        height: 10,
        borderRadius: '50%',
        background: cor || '#64748b',
        marginRight: 6,
        flexShrink: 0,
        verticalAlign: 'middle',
      }}
      title={nome}
    />
  )
}
