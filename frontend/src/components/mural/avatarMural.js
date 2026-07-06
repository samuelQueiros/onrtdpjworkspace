const AVATAR_COLORS = [
  '#4f86c6', '#e07b54', '#5aab7f', '#a06bbf',
  '#c4a93e', '#d9534f', '#5bc0de', '#3d8b6e',
]

export function getInitials(nome) {
  const parts = nome.trim().split(/\s+/)
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export function avatarColor(nome) {
  let hash = 0
  for (const char of nome) hash = (hash * 31 + char.charCodeAt(0)) & 0xffff
  return AVATAR_COLORS[hash % AVATAR_COLORS.length]
}
