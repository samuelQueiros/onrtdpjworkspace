export default function UserColorDot({ color, size = 18 }) {
  return (
    <span
      style={{
        display: 'inline-block',
        width: size,
        height: size,
        borderRadius: '50%',
        background: color || '#e2e8f0',
        border: '1.5px solid rgba(0,0,0,.1)',
        verticalAlign: 'middle',
      }}
      title={color || 'Sem cor'}
    />
  )
}
