from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.patrimonio import (
    BaixaCreate,
    DesvinculoCreate,
    EquipamentoCreate,
    EquipamentoDetalheOut,
    EquipamentoOut,
    EquipamentosPageOut,
    ManutencaoCreate,
    VinculoCreate,
    EquipamentoUpdate,
)
from app.services import patrimonios_service

router = APIRouter(prefix="/patrimonios", tags=["Patrimonios"])


@router.get("", response_model=EquipamentosPageOut)
def listar_equipamentos(
    busca: str | None = None,
    tipo: str | None = None,
    status_equipamento: str | None = Query(default=None, alias="status"),
    ativo: bool | None = None,
    user_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return patrimonios_service.listar_equipamentos(
        db, busca, tipo, status_equipamento, ativo, user_id, page, page_size
    )


@router.post("", response_model=EquipamentoOut, status_code=status.HTTP_201_CREATED)
def criar_equipamento(
    payload: EquipamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.criar_equipamento(db, payload, current_user)


@router.get("/me", response_model=list[EquipamentoOut])
def meus_equipamentos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return patrimonios_service.meus_equipamentos(db, current_user)


@router.get("/disponiveis", response_model=list[EquipamentoOut])
def equipamentos_disponiveis(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return patrimonios_service.equipamentos_disponiveis(db)


@router.get("/{equipamento_id}", response_model=EquipamentoDetalheOut)
def detalhe_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return patrimonios_service.obter_detalhe(db, equipamento_id)


@router.put("/{equipamento_id}", response_model=EquipamentoOut)
def editar_equipamento(
    equipamento_id: int,
    payload: EquipamentoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.editar_equipamento(db, equipamento_id, payload, current_user)


@router.post("/{equipamento_id}/vinculos", response_model=EquipamentoOut)
def vincular_equipamento(
    equipamento_id: int,
    payload: VinculoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.vincular_equipamento(db, equipamento_id, payload, current_user)


@router.post("/{equipamento_id}/desvincular", response_model=EquipamentoOut)
def desvincular_equipamento(
    equipamento_id: int,
    payload: DesvinculoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.desvincular_equipamento(db, equipamento_id, payload, current_user)


@router.post("/{equipamento_id}/manutencao", response_model=EquipamentoOut)
def iniciar_manutencao(
    equipamento_id: int,
    payload: ManutencaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.iniciar_manutencao(db, equipamento_id, payload, current_user)


@router.post("/{equipamento_id}/finalizar-manutencao", response_model=EquipamentoOut)
def finalizar_manutencao(
    equipamento_id: int,
    payload: ManutencaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.finalizar_manutencao(db, equipamento_id, payload, current_user)


@router.post("/{equipamento_id}/baixa", response_model=EquipamentoOut)
def baixar_equipamento(
    equipamento_id: int,
    payload: BaixaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return patrimonios_service.baixar_equipamento(db, equipamento_id, payload, current_user)
