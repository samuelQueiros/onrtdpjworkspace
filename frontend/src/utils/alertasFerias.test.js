import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  avisoFeriasDismissKey,
  limparAvisosFeriasDispensados,
} from './alertasFerias'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('alertas de férias por sessão', () => {
  it('gera uma chave estável para o alerta dispensado', () => {
    expect(avisoFeriasDismissKey(42)).toBe('ferias-4dias-dismissed-42')
  })

  it('limpa apenas dispensas de férias ao iniciar um novo login', () => {
    const storage = {
      'ferias-4dias-dismissed-42': '1',
      'birthday-shown-1': '1',
      removeItem(key) {
        delete this[key]
      },
    }
    vi.stubGlobal('sessionStorage', storage)

    limparAvisosFeriasDispensados()

    expect(storage['ferias-4dias-dismissed-42']).toBeUndefined()
    expect(storage['birthday-shown-1']).toBe('1')
  })
})
