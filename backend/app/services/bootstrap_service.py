import json
from datetime import date

from sqlalchemy.orm import Session

from app.core.crypto import criptografar_dado_sensivel, hash_dado_sensivel
from app.core.config import settings
from app.core.security import hash_senha
from app.models.cargo import Cargo
from app.models.departamento import Departamento
from app.models.log import Log
from app.models.user import User
from app.repositories import bootstrap_repository
from app.storage.documentos_storage import inicializar_diretorios_upload

TEST_USERS = (
    {"nome": "Ana Teste", "email": "ana.teste@sistema.local", "cpf": "52998224725", "cor": "#2563EB", "data_admissao": date(2024, 1, 15), "data_aniversario": date(1992, 3, 10), "telefone": "(11) 99999-1001"},
    {"nome": "Bruno Teste", "email": "bruno.teste@sistema.local", "cpf": "11144477735", "cor": "#16A34A", "data_admissao": date(2023, 6, 5), "data_aniversario": date(1988, 7, 22), "telefone": "(11) 99999-1002"},
    {"nome": "Carla Teste", "email": "carla.teste@sistema.local", "cpf": "12345678909", "cor": "#9333EA", "data_admissao": date(2022, 9, 12), "data_aniversario": date(1995, 11, 8), "telefone": "(11) 99999-1003"},
)


def inicializar_uploads() -> None:
    inicializar_diretorios_upload()


def garantir_admin_inicial(db: Session) -> str:
    if bootstrap_repository.obter_admin(db):
        return "admin_existente"

    admin_email = settings.admin_email
    admin_password = settings.admin_password

    if not admin_email or not admin_password:
        return "admin_nao_configurado"

    if len(admin_password) < 8:
        raise RuntimeError("ADMIN_PASSWORD deve ter pelo menos 8 caracteres.")
    if settings.environment == "production":
        fracas = {"admin123", "password", "12345678", "administrador"}
        if len(admin_password) < 12 or admin_password.lower() in fracas:
            raise RuntimeError("ADMIN_PASSWORD deve ser forte e ter pelo menos 12 caracteres em producao.")

    admin = User(
        nome=settings.admin_name,
        email=admin_email,
        senha_hash=hash_senha(admin_password),
        role="admin",
        dias_totais=30,
    )
    log = Log(
        user_id=None,
        acao="USUARIO_CRIADO",
        detalhes="Administrador inicial criado automaticamente.",
    )
    bootstrap_repository.salvar_admin_com_log(db, admin, log)
    return "admin_criado"


def garantir_usuarios_teste(db: Session) -> int:
    if not settings.create_test_users:
        return 0

    password = settings.test_user_password
    if not password or len(password) < 8:
        raise RuntimeError(
            "TEST_USER_PASSWORD deve ser configurada e ter pelo menos 8 caracteres "
            "quando CREATE_TEST_USERS=true."
        )

    departamento = db.query(Departamento).filter(
        Departamento.nome == "Departamento Teste"
    ).first()
    if not departamento:
        departamento = Departamento(nome="Departamento Teste", limite_simultaneo=2)
        db.add(departamento)
        db.flush()

    cargo = db.query(Cargo).filter(Cargo.nome == "Desenvolvedor").first()
    if not cargo:
        cargo = Cargo(nome="Desenvolvedor")
        db.add(cargo)
        db.flush()

    endereco = criptografar_dado_sensivel(json.dumps({
        "logradouro": "Rua de Teste",
        "numero": "100",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "cep": "01001-000",
    }, ensure_ascii=False, separators=(",", ":")))
    criados = 0
    for indice, dados in enumerate(TEST_USERS, start=1):
        if db.query(User).filter(User.email == dados["email"]).first():
            continue

        cpf_hash = hash_dado_sensivel(dados["cpf"])
        if db.query(User).filter(User.cpf_hash == cpf_hash).first():
            continue

        dados_bancarios = criptografar_dado_sensivel(json.dumps({
            "banco": "Banco Teste",
            "agencia": "0001",
            "conta": f"1000{indice}-0",
            "cpf_titular": dados["cpf"],
            "nome_titular": dados["nome"],
            "chave_pix": dados["email"],
        }, ensure_ascii=False, separators=(",", ":")))
        user = User(
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=hash_senha(password),
            role="user",
            dias_totais=30,
            departamento_id=departamento.id,
            cargo_id=cargo.id,
            data_admissao=dados["data_admissao"],
            data_aniversario=dados["data_aniversario"],
            cor=dados["cor"],
            telefone=dados["telefone"],
            telefone_emergencia="(11) 98888-0001",
            telefone_emergencia_2="(11) 97777-0001",
            endereco=endereco,
            dados_bancarios=dados_bancarios,
            cpf_criptografado=criptografar_dado_sensivel(dados["cpf"]),
            cpf_hash=cpf_hash,
        )
        db.add(user)
        db.flush()
        db.add(Log(
            user_id=user.id,
            acao="USUARIO_CRIADO",
            detalhes=f"Usuario de teste {user.nome} criado automaticamente.",
        ))
        criados += 1

    db.commit()
    return criados
