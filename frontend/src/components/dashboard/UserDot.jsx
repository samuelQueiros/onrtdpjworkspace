export default function UserDot({ cor, nome, size = 10 }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: size,
        height: size,
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
