// Uma "correcao" conserta um valor de um reajuste já registrado (não conta
// como evento de carreira novo), mas ainda assim precisa ser refletida no
// valor exibido do reajuste que ela corrige. Não existe vínculo estrutural
// no banco entre a correção e o reajuste — a correção mais recente depois
// de um reajuste (e antes do próximo, se houver) é aplicada por cima dele.
export function aplicarCorrecoesSalariais(historicoSalarial) {
  const ordenado = [...(historicoSalarial || [])].sort(
    (a, b) => new Date(a.criado_em) - new Date(b.criado_em),
  )

  const reajustes = []
  let atual = null
  for (const item of ordenado) {
    if (item.tipo === 'reajuste') {
      atual = { ...item }
      reajustes.push(atual)
    } else if (item.tipo === 'correcao' && atual) {
      atual.salario = item.salario
    }
  }
  return reajustes
}
