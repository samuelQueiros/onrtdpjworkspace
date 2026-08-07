from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.departamento import Departamento
from app.models.user import User
from app.repositories import departamentos_repository
from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate
from app.services import log_service


def formatar_departamento(db: Session, departamento: Departamento, incluir_total: bool = False) -> dict:
    dados = {
        "id": departamento.id,
        "nome": departamento.nome,
        "limite_simultaneo": departamento.limite_simultaneo,
        "criado_em": departamento.criado_em,
    }

    if incluir_total:
        dados["total_usuarios"] = departamentos_repository.contar_usuarios_por_departamento(db, departamento.id)

    return dados


def buscar_departamento(db: Session, departamento_id: int) -> Departamento:
    departamento = departamentos_repository.obter_departamento_por_id(db, departamento_id)
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return departamento


def validar_nome_disponivel(db: Session, nome: str, departamento_id: int | None = None) -> None:
    if departamento_id is None:
        existente = departamentos_repository.obter_departamento_por_nome(db, nome)
    else:
        existente = departamentos_repository.obter_departamento_por_nome_exceto_id(db, nome, departamento_id)

    if existente:
        raise HTTPException(status_code=400, detail="Já existe um departamento com esse nome")


def listar_departamentos(db: Session) -> list[dict]:
    return [
        formatar_departamento(db, departamento, incluir_total=True)
        for departamento in departamentos_repository.listar_departamentos(db)
    ]


def criar_departamento(db: Session, payload: DepartamentoCreate, current_user: User) -> dict:
    validar_nome_disponivel(db, payload.nome)

    departamento = Departamento(
        nome=payload.nome,
        limite_simultaneo=payload.limite_simultaneo,
    )
    log = log_service.construir_log(
        current_user,
        acao="DEPARTAMENTO_CRIADO",
        detalhes=f"Departamento '{departamento.nome}' criado (limite: {departamento.limite_simultaneo})",
    )
    departamentos_repository.salvar_departamento_com_log(db, departamento, log)
    return formatar_departamento(db, departamento)


def editar_departamento(db: Session, departamento_id: int, payload: DepartamentoUpdate, current_user: User) -> dict:
    departamento = buscar_departamento(db, departamento_id)

    if payload.nome is not None:
        validar_nome_disponivel(db, payload.nome, departamento_id)
        departamento.nome = payload.nome

    if payload.limite_simultaneo is not None:
        departamento.limite_simultaneo = payload.limite_simultaneo

    log = log_service.construir_log(
        current_user,
        acao="DEPARTAMENTO_EDITADO",
        detalhes=f"Departamento #{departamento_id} atualizado",
    )
    departamentos_repository.atualizar_departamento_com_log(db, departamento, log)
    return formatar_departamento(db, departamento)


def excluir_departamento(db: Session, departamento_id: int, current_user: User) -> None:
    departamento = buscar_departamento(db, departamento_id)
    log = log_service.construir_log(
        current_user,
        acao="DEPARTAMENTO_EXCLUIDO",
        detalhes=f"Departamento '{departamento.nome}' excluído",
    )
    departamentos_repository.excluir_departamento_com_log(db, departamento, log)
