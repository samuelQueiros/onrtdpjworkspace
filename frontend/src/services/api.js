import { alertasService } from './dominios/alertasService'
import { authService } from './dominios/authService'
import { avisosService } from './dominios/avisosService'
import { bloqueiosService } from './dominios/bloqueiosService'
import { credenciaisService } from './dominios/credenciaisService'
import { cargosService } from './dominios/cargosService'
import { departamentosService } from './dominios/departamentosService'
import { documentosService } from './dominios/documentosService'
import { feriasService } from './dominios/feriasService'
import { importacaoService } from './dominios/importacaoService'
import { relatoriosService } from './dominios/relatoriosService'
import { usersService } from './dominios/usersService'
import { patrimoniosService } from './dominios/patrimoniosService'
import { autorizacoesEquipamentosService } from './dominios/autorizacoesEquipamentosService'

export const api = {
  ...authService,
  ...feriasService,
  ...usersService,
  ...departamentosService,
  ...avisosService,
  ...documentosService,
  ...relatoriosService,
  ...importacaoService,
  ...bloqueiosService,
  ...alertasService,
  ...credenciaisService,
  ...cargosService,
  ...patrimoniosService,
  ...autorizacoesEquipamentosService,
}
