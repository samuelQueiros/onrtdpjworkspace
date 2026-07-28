import { describe, expect, it } from 'vitest'

import { overlaps, validarDataInicio } from './feriasValidation'

describe('feriasValidation', () => {
  it('detecta sobreposição inclusiva de períodos', () => {
    expect(overlaps('2026-08-10', '2026-08-15', {
      data_inicio: '2026-08-15',
      data_fim: '2026-08-20',
    })).toBe(true)
  })

  it('rejeita um período cuja data final antecede a inicial', () => {
    expect(validarDataInicio('2099-08-10', '2099-08-09', new Set()))
      .toBe('A data de fim não pode ser anterior à data de início.')
  })
})
