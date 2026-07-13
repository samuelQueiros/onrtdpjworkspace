from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_senha, verificar_senha
from app.core.crypto import criptografar_dado_sensivel, descriptografar_dado_sensivel
from app.models.log import Log
from app.models.user import User
from app.repositories import users_repository
from app.schemas.user import UserConfigUpdate, UserCreate, UserUpdate
from app.services import cargos_service


def calcular_dias_restantes(user: User, db: Session) -> int:
    from app.services.ferias_service import calcular_saldo

    return calcular_saldo(db, user)


def formatar_usuario(user: User, db: Session) -> dict:
    departamento = None
    if user.departamento_id:
        dep = user.departamento
        departamento = {"id": dep.id, "nome": dep.nome} if dep else None

    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role,
        "dias_totais": user.dias_totais,
        "dias_restantes": calcular_dias_restantes(user, db),
        "departamento_id": user.departamento_id,
        "departamento": departamento,
        "data_admissao": user.data_admissao,
        "data_aniversario": user.data_aniversario,
        "cor": user.cor,
        "telefone": user.telefone,
        "cargo": user.cargo.nome if user.cargo else None,
        "ativo": user.ativo,
        "criado_em": user.criado_em,
    }


def formatar_dados_sensiveis(user: User) -> dict:
    return {
        "telefone_emergencia": user.telefone_emergencia,
        "endereco": user.endereco,
        "dados_bancarios": descriptografar_dado_sensivel(user.dados_bancarios),
    }


def buscar_usuario(db: Session, user_id: int) -> User:
    user = users_repository.obter_usuario_por_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return user


def validar_email_disponivel(db: Session, email: str, user_id: int | None = None) -> None:
    if user_id is None:
        existente = users_repository.obter_usuario_por_email(db, email)
        if existente:
            raise HTTPException(status_code=400, detail="E-mail ja cadastrado")
        return

    existente = users_repository.obter_usuario_por_email_exceto_id(db, email, user_id)
    if existente:
        raise HTTPException(status_code=400, detail="E-mail ja em uso por outro usuario")


def validar_departamento(db: Session, departamento_id: int | None) -> None:
    if departamento_id and not users_repository.obter_departamento_por_id(db, departamento_id):
        raise HTTPException(status_code=404, detail="Departamento nao encontrado")


def listar_usuarios(db: Session) -> list[dict]:
    return [formatar_usuario(user, db) for user in users_repository.listar_usuarios(db)]


def criar_usuario(db: Session, payload: UserCreate, current_user: User) -> dict:
    validar_email_disponivel(db, payload.email)
    validar_departamento(db, payload.departamento_id)
    cargo = cargos_service.obter_cargo_por_nome(db, payload.cargo)

    novo_user = User(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        role=payload.role,
        dias_totais=payload.dias_totais,
        departamento_id=payload.departamento_id,
        data_admissao=payload.data_admissao,
        data_aniversario=payload.data_aniversario,
        cor=payload.cor,
        telefone=payload.telefone,
        telefone_emergencia=payload.telefone_emergencia,
        endereco=payload.endereco,
        dados_bancarios=(
            criptografar_dado_sensivel(payload.dados_bancarios.strip())
            if payload.dados_bancarios and payload.dados_bancarios.strip()
            else None
        ),
        cargo_id=cargo.id if cargo else None,
    )

    log = Log(
        user_id=novo_user.id,
        acao="USUARIO_CRIADO",
        detalhes=f"Usuario {novo_user.nome} ({novo_user.email}) criado por {current_user.nome}",
    )
    users_repository.salvar_usuario_com_log(db, novo_user, log)

    return formatar_usuario(novo_user, db)


def editar_usuario(db: Session, user_id: int, payload: UserUpdate, current_user: User) -> dict:
    user = buscar_usuario(db, user_id)

    if payload.nome is not None:
        user.nome = payload.nome
    if payload.email is not None:
        validar_email_disponivel(db, payload.email, user_id)
        user.email = payload.email
    if payload.dias_totais is not None:
        user.dias_totais = payload.dias_totais
    if payload.departamento_id is not None:
        if payload.departamento_id == 0:
            user.departamento_id = None
        else:
            validar_departamento(db, payload.departamento_id)
            user.departamento_id = payload.departamento_id
    if payload.data_admissao is not None:
        user.data_admissao = payload.data_admissao
    if payload.data_aniversario is not None:
        user.data_aniversario = payload.data_aniversario
    if payload.senha is not None and payload.senha.strip():
        user.senha_hash = hash_senha(payload.senha)
    if payload.cor is not None:
        user.cor = payload.cor if payload.cor.strip() else None
    if "telefone" in payload.model_fields_set:
        user.telefone = payload.telefone.strip() if payload.telefone and payload.telefone.strip() else None
    if "telefone_emergencia" in payload.model_fields_set:
        user.telefone_emergencia = (
            payload.telefone_emergencia.strip()
            if payload.telefone_emergencia and payload.telefone_emergencia.strip()
            else None
        )
    if "endereco" in payload.model_fields_set:
        user.endereco = payload.endereco.strip() if payload.endereco and payload.endereco.strip() else None
    if "dados_bancarios" in payload.model_fields_set:
        user.dados_bancarios = (
            criptografar_dado_sensivel(payload.dados_bancarios.strip())
            if payload.dados_bancarios and payload.dados_bancarios.strip()
            else None
        )
    if "cargo" in payload.model_fields_set:
        cargo = cargos_service.obter_cargo_por_nome(db, payload.cargo)
        user.cargo_id = cargo.id if cargo else None
    if payload.ativo is not None:
        user.ativo = payload.ativo

    log = Log(
        user_id=current_user.id,
        acao="USUARIO_EDITADO",
        detalhes=f"Usuario {user.nome} ({user.email}) editado por {current_user.nome}",
    )
    users_repository.atualizar_usuario_com_log(db, user, log)

    return formatar_usuario(user, db)


def listar_aniversariantes(db: Session) -> list[dict]:
    hoje = date.today()
    return [
        {
            "nome": user.nome,
            "data_aniversario": user.data_aniversario,
        }
        for user in users_repository.listar_usuarios_com_aniversario(db)
        if user.data_aniversario and user.data_aniversario.month == hoje.month
    ]


def desativar_usuario(db: Session, user_id: int, current_user: User) -> None:
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Voce nao pode excluir sua propria conta")

    user = buscar_usuario(db, user_id)
    if not user.ativo:
        return
    user.ativo = False
    log = Log(
        user_id=current_user.id,
        acao="USUARIO_DESATIVADO",
        detalhes=f"Usuario {user.nome} ({user.email}) desativado por {current_user.nome}",
    )
    users_repository.atualizar_usuario_com_log(db, user, log)


def atualizar_configuracoes(db: Session, payload: UserConfigUpdate, current_user: User) -> dict:
    if payload.nome is not None:
        current_user.nome = payload.nome
    if payload.email is not None:
        validar_email_disponivel(db, payload.email, current_user.id)
        current_user.email = payload.email

    if payload.nova_senha is not None and payload.nova_senha.strip():
        if not payload.senha_atual:
            raise HTTPException(status_code=400, detail="Informe a senha atual para altera-la")
        if not verificar_senha(payload.senha_atual, current_user.senha_hash):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")
        current_user.senha_hash = hash_senha(payload.nova_senha)

    users_repository.salvar_usuario(db, current_user)
    return formatar_usuario(current_user, db)
