import io
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ferias import Ferias
from app.models.log import Log
from app.models.user import User
from app.repositories import importacao_repository
from app.services import ferias_service

MAX_IMPORT_SIZE = 5 * 1024 * 1024


def parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value

    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_datetime(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value

    text = str(value).strip()
    for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def validar_extensao_planilha(filename: str | None) -> None:
    if not filename or not filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .xlsx")


def parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    texto = str(value).strip().lower()
    if texto in {"1", "sim", "s", "true", "verdadeiro"}:
        return True
    if texto in {"0", "nao", "não", "n", "false", "falso", ""}:
        return False
    raise ValueError(f"valor booleano invalido: {value}")


def carregar_linhas_planilha(conteudo: bytes) -> list[tuple]:
    try:
        import openpyxl
    except ImportError as exc:
        raise HTTPException(status_code=500, detail="Biblioteca openpyxl nao instalada no servidor") from exc

    try:
        wb = openpyxl.load_workbook(io.BytesIO(conteudo), read_only=True, data_only=True)
        ws = wb.active
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {exc}") from exc

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="Planilha vazia")
    return rows


def ignorar_cabecalho(rows: list[tuple]) -> list[tuple]:
    header = rows[0]
    return rows[1:] if header and isinstance(header[0], str) and not parse_date(header[0]) else rows


def importar_ferias(db: Session, filename: str | None, conteudo: bytes, current_user: User) -> dict:
    validar_extensao_planilha(filename)
    data_rows = ignorar_cabecalho(carregar_linhas_planilha(conteudo))

    inseridos = 0
    erros: list[str] = []

    for i, row in enumerate(data_rows, start=2):
        if len(row) < 3:
            erros.append(f"Linha {i}: colunas insuficientes (esperado email, data_inicio, data_fim)")
            continue

        email_val, inicio_val, fim_val = row[0], row[1], row[2]
        try:
            ferias_acordo = parse_bool(row[3] if len(row) > 3 else None)
        except ValueError as exc:
            erros.append(f"Linha {i}: {exc}")
            continue

        user = importacao_repository.obter_usuario_por_email(db, str(email_val).strip())
        if not user:
            erros.append(f"Linha {i}: usuario '{email_val}' nao encontrado")
            continue

        data_inicio = parse_date(inicio_val)
        data_fim = parse_date(fim_val)
        if not data_inicio or not data_fim:
            erros.append(f"Linha {i}: datas invalidas ({inicio_val} / {fim_val})")
            continue

        if data_fim < data_inicio:
            erros.append(f"Linha {i}: data_fim anterior a data_inicio")
            continue

        if importacao_repository.existe_ferias_periodo(db, user.id, data_inicio, data_fim):
            erros.append(f"Linha {i}: periodo {data_inicio}-{data_fim} ja existe para {email_val}")
            continue

        try:
            ferias_service.bloquear_regras_ferias(db, user)
            ferias_service.verificar_regras_data(data_inicio, data_fim)
            ferias_service.verificar_bloqueio_datas(db, data_inicio, data_fim)
            dias = ferias_service.calcular_dias(data_inicio, data_fim)
            if not ferias_acordo:
                if ferias_service.verificar_sobreposicao_departamento(db, user, data_inicio, data_fim):
                    raise HTTPException(status_code=400, detail="limite simultaneo do departamento atingido")
                saldo = ferias_service.calcular_saldo(db, user)
                if saldo < dias:
                    raise HTTPException(status_code=400, detail=f"saldo insuficiente ({saldo} dias)")
        except HTTPException as exc:
            erros.append(f"Linha {i}: {exc.detail}")
            continue
        importacao_repository.adicionar_ferias(
            db,
            Ferias(
                user_id=user.id,
                data_inicio=data_inicio,
                data_fim=data_fim,
                dias_usados=dias,
                status="aprovada",
                ferias_acordo=ferias_acordo,
            ),
        )
        inseridos += 1

    if inseridos:
        importacao_repository.adicionar_log(
            db,
            Log(
                user_id=current_user.id,
                acao="FERIAS_IMPORTADAS",
                detalhes=f"{inseridos} periodo(s) importado(s) via Excel",
            ),
        )
        importacao_repository.commit(db)

    return {
        "inseridos": inseridos,
        "erros": erros,
        "mensagem": f"{inseridos} registro(s) importado(s) com sucesso. {len(erros)} erro(s).",
    }


def importar_logs(db: Session, filename: str | None, conteudo: bytes, current_user: User) -> dict:
    validar_extensao_planilha(filename)
    data_rows = ignorar_cabecalho(carregar_linhas_planilha(conteudo))

    inseridos = 0
    erros: list[str] = []

    for i, row in enumerate(data_rows, start=2):
        if len(row) < 3:
            erros.append(f"Linha {i}: colunas insuficientes (esperado data, acao, detalhes)")
            continue

        data_val, acao_val, detalhes_val = row[0], row[1], row[2]
        email_val = row[3] if len(row) > 3 else None

        user_id = None
        if email_val:
            user = importacao_repository.obter_usuario_por_email(db, str(email_val).strip())
            if user:
                user_id = user.id

        importacao_repository.adicionar_log(
            db,
            Log(
                user_id=user_id,
                acao=str(acao_val).strip() if acao_val else "IMPORTADO",
                detalhes=str(detalhes_val).strip() if detalhes_val else None,
                criado_em=parse_datetime(data_val) or datetime.utcnow(),
            ),
        )
        inseridos += 1

    if inseridos:
        importacao_repository.commit(db)

    return {
        "inseridos": inseridos,
        "erros": erros,
        "mensagem": f"{inseridos} log(s) importado(s) com sucesso. {len(erros)} erro(s).",
    }
