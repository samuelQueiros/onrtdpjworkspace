from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cargo import Cargo
from app.models.user import User
from app.repositories import cargos_repository
from app.schemas.cargo import CargoCreate, CargoUpdate
from app.services import log_service


def _nome_limpo(nome: str) -> str:
    return " ".join(nome.split())


def _formatar(db: Session, cargo: Cargo) -> dict:
    return {
        "id": cargo.id,
        "nome": cargo.nome,
        "total_usuarios": cargos_repository.contar_usuarios(db, cargo.id),
        "criado_em": cargo.criado_em,
    }


def listar_cargos(db: Session) -> list[dict]:
    return [_formatar(db, cargo) for cargo in cargos_repository.listar_cargos(db)]


def obter_cargo_por_nome(db: Session, nome: str | None) -> Cargo | None:
    if not nome:
        return None
    cargo = cargos_repository.obter_cargo_por_nome(db, nome)
    if not cargo:
        raise HTTPException(status_code=400, detail="Cargo não cadastrado")
    return cargo


def criar_cargo(db: Session, payload: CargoCreate, current_user: User) -> dict:
    nome = _nome_limpo(payload.nome)
    if cargos_repository.obter_cargo_por_nome(db, nome):
        raise HTTPException(status_code=400, detail="Já existe um cargo com esse nome")
    cargo = Cargo(nome=nome)
    log = log_service.construir_log(current_user, acao="CARGO_CRIADO", detalhes=f"Cargo '{nome}' criado")
    cargos_repository.salvar_com_log(db, cargo, log)
    return _formatar(db, cargo)


def editar_cargo(db: Session, cargo_id: int, payload: CargoUpdate, current_user: User) -> dict:
    cargo = cargos_repository.obter_cargo_por_id(db, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    nome = _nome_limpo(payload.nome)
    if cargos_repository.obter_cargo_por_nome_exceto_id(db, nome, cargo_id):
        raise HTTPException(status_code=400, detail="Já existe um cargo com esse nome")
    cargo.nome = nome
    log = log_service.construir_log(current_user, acao="CARGO_EDITADO", detalhes=f"Cargo #{cargo_id} renomeado para '{nome}'")
    cargos_repository.atualizar_com_log(db, cargo, log)
    return _formatar(db, cargo)


def excluir_cargo(db: Session, cargo_id: int, current_user: User) -> None:
    cargo = cargos_repository.obter_cargo_por_id(db, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    log = log_service.construir_log(current_user, acao="CARGO_EXCLUIDO", detalhes=f"Cargo '{cargo.nome}' excluído")
    cargos_repository.excluir_com_log(db, cargo, log)
