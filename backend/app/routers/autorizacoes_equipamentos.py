from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.database import get_db
from app.models.ferias import Ferias
from app.models.user import User
from app.schemas.patrimonio import (
    AceiteSolicitacaoCreate,
    AprovacaoSolicitacaoCreate,
    CancelamentoSolicitacaoCreate,
    DevolucaoSolicitacaoCreate,
    EntregaSolicitacaoCreate,
    PendenciasAprovacaoOut,
    RejeicaoSolicitacaoCreate,
    SolicitacaoEquipamentoCreate,
    SolicitacaoEquipamentoOut,
)
from app.services import autorizacoes_equipamentos_service

router = APIRouter(prefix="/autorizacoes-equipamentos", tags=["Autorizacoes de equipamentos"])
pendencias_router = APIRouter(prefix="/aprovacoes", tags=["Aprovacoes"])


@router.post("", response_model=SolicitacaoEquipamentoOut, status_code=status.HTTP_201_CREATED)
def criar_solicitacao(
    payload: SolicitacaoEquipamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return autorizacoes_equipamentos_service.criar_solicitacao(db, payload, current_user)


@router.get("/me", response_model=list[SolicitacaoEquipamentoOut])
def minhas_solicitacoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return autorizacoes_equipamentos_service.listar_minhas_solicitacoes(db, current_user)


@router.get("/admin", response_model=list[SolicitacaoEquipamentoOut])
def listar_solicitacoes_admin(
    status_solicitacao: str | None = Query(default=None, alias="status"),
    user_id: int | None = None,
    equipamento_id: int | None = None,
    criado_de: datetime | None = None,
    criado_ate: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.listar_solicitacoes_admin(
        db, current_user, status_solicitacao, user_id, equipamento_id, criado_de, criado_ate
    )


@router.get("/{solicitacao_id}", response_model=SolicitacaoEquipamentoOut)
def obter_solicitacao(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    solicitacao = autorizacoes_equipamentos_service.buscar_solicitacao(db, solicitacao_id, current_user)
    return autorizacoes_equipamentos_service.formatar_solicitacao(solicitacao, current_user)


@router.post("/{solicitacao_id}/cancelar", response_model=SolicitacaoEquipamentoOut)
def cancelar_solicitacao(
    solicitacao_id: int,
    payload: CancelamentoSolicitacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return autorizacoes_equipamentos_service.cancelar_solicitacao(
        db, solicitacao_id, payload, current_user
    )


@router.post("/{solicitacao_id}/aprovar", response_model=SolicitacaoEquipamentoOut)
def aprovar_solicitacao(
    solicitacao_id: int,
    payload: AprovacaoSolicitacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.aprovar_solicitacao(
        db, solicitacao_id, payload, current_user
    )


@router.post("/{solicitacao_id}/rejeitar", response_model=SolicitacaoEquipamentoOut)
def rejeitar_solicitacao(
    solicitacao_id: int,
    payload: RejeicaoSolicitacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.rejeitar_solicitacao(
        db, solicitacao_id, payload, current_user
    )


@router.post("/{solicitacao_id}/entrega", response_model=SolicitacaoEquipamentoOut)
def registrar_entrega(
    solicitacao_id: int,
    payload: EntregaSolicitacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.registrar_entrega(
        db, solicitacao_id, payload, current_user
    )


@router.post("/{solicitacao_id}/aceite", response_model=SolicitacaoEquipamentoOut)
def registrar_aceite(
    solicitacao_id: int,
    payload: AceiteSolicitacaoCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return autorizacoes_equipamentos_service.registrar_aceite(
        db, solicitacao_id, payload, current_user, request
    )


@router.post("/{solicitacao_id}/devolucao", response_model=SolicitacaoEquipamentoOut)
def registrar_devolucao(
    solicitacao_id: int,
    payload: DevolucaoSolicitacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.registrar_devolucao(
        db, solicitacao_id, payload, current_user
    )


@router.post("/{solicitacao_id}/documento/regenerar", response_model=SolicitacaoEquipamentoOut)
def regenerar_documento(
    solicitacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return autorizacoes_equipamentos_service.regenerar_documento(db, solicitacao_id, current_user)


@pendencias_router.get("/pendencias", response_model=PendenciasAprovacaoOut)
def contar_pendencias(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    ferias = db.query(Ferias).filter(Ferias.status == "pendente").count()
    equipamentos = autorizacoes_equipamentos_service.contar_pendentes(db)
    return {"ferias": ferias, "equipamentos": equipamentos, "total": ferias + equipamentos}
