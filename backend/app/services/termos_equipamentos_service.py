import base64
import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from jinja2 import Environment, StrictUndefined, select_autoescape
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.cpf import formatar_cpf, validar_cpf
from app.core.crypto import criptografar_dado_sensivel, descriptografar_dado_sensivel
from app.models.documento import Documento
from app.models.patrimonio import SolicitacaoEquipamento, TermoEquipamentoVersao
from app.models.user import User
from app.repositories import patrimonios_repository
from app.services import log_service
from app.storage.documentos_storage import caminho_documento
from app.storage.termos_storage import (
    confirmar_termo_pdf,
    montar_nome_arquivo_termo,
    reverter_termo_pdf,
    salvar_termo_pdf,
)


TERMO_VERSAO_CODIGO = "v2"
FUSO_SAO_PAULO = ZoneInfo("America/Sao_Paulo")
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "termos_equipamentos"
TEMPLATE_PATH = TEMPLATE_DIR / f"{TERMO_VERSAO_CODIGO}.html"
CLAUSULAS_PATH = TEMPLATE_DIR / f"{TERMO_VERSAO_CODIGO}_clausulas.txt"
LOGO_PATH = TEMPLATE_DIR / "onrtdpj.png"

TIPOS_LABEL = {
    "notebook": "Notebook",
    "desktop": "Desktop",
    "monitor": "Monitor",
    "mouse": "Mouse",
    "teclado": "Teclado",
    "headset": "Headset",
    "dock_station": "Dock Station",
    "carregador": "Carregador",
    "cabo_energia": "Cabo de energia",
    "adaptador": "Adaptadores",
    "outro": "Outros",
}

MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

_JINJA = Environment(
    autoescape=select_autoescape(enabled_extensions=("html", "xml"), default_for_string=True),
    undefined=StrictUndefined,
    auto_reload=False,
    trim_blocks=True,
    lstrip_blocks=True,
)


class TermoEquipamentoError(RuntimeError):
    """Falha de domínio ou de renderização do termo de equipamentos."""


@dataclass(frozen=True, slots=True)
class TermoGerado:
    versao_codigo: str
    conteudo_hash: str
    html: str
    pdf_bytes: bytes
    pdf_hash: str
    nome_arquivo: str


def _caminhos_versao(codigo: str) -> tuple[Path, Path]:
    if not codigo or not codigo.replace("_", "").replace("-", "").isalnum():
        raise TermoEquipamentoError("Código de versão de termo inválido.")
    if codigo == TERMO_VERSAO_CODIGO:
        return TEMPLATE_PATH, CLAUSULAS_PATH
    return TEMPLATE_DIR / f"{codigo}.html", TEMPLATE_DIR / f"{codigo}_clausulas.txt"


def obter_conteudo_template(codigo: str = TERMO_VERSAO_CODIGO) -> str:
    template_path, _ = _caminhos_versao(codigo)
    try:
        conteudo = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TermoEquipamentoError("Template do termo de equipamentos não encontrado.") from exc
    # O hash nao pode variar apenas por conversao LF/CRLF entre Linux e Windows.
    return conteudo.replace("\r\n", "\n").replace("\r", "\n")


def obter_hash_template(codigo: str = TERMO_VERSAO_CODIGO) -> str:
    """Identifica a versão visual e textual, incluindo o logotipo usado."""
    digest = hashlib.sha256()
    try:
        digest.update(obter_conteudo_template(codigo).encode("utf-8"))
        digest.update(b"\0logo\0")
        digest.update(LOGO_PATH.read_bytes())
        digest.update(b"\0clausulas\0")
        digest.update(obter_clausulas_termo(codigo).encode("utf-8"))
    except OSError as exc:
        raise TermoEquipamentoError("Recursos do termo de equipamentos não encontrados.") from exc
    return digest.hexdigest()


def obter_clausulas_termo(codigo: str = TERMO_VERSAO_CODIGO) -> str:
    _, clausulas_path = _caminhos_versao(codigo)
    try:
        conteudo = clausulas_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TermoEquipamentoError("Cláusulas do termo de equipamentos não encontradas.") from exc
    return conteudo.replace("\r\n", "\n").replace("\r", "\n").strip()


def obter_metadados_versao() -> dict[str, str]:
    return {
        "codigo": TERMO_VERSAO_CODIGO,
        "conteudo_hash": obter_hash_template(),
        "clausulas": obter_clausulas_termo(),
    }


def _em_sao_paulo(valor: datetime | None, campo: str) -> datetime:
    if valor is None:
        raise TermoEquipamentoError(f"{campo} deve estar registrado antes da geração do termo.")
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=UTC)
    return valor.astimezone(FUSO_SAO_PAULO)


def _formatar_data(valor: datetime | None, campo: str) -> str:
    return _em_sao_paulo(valor, campo).strftime("%d/%m/%Y")


def _formatar_data_hora(valor: datetime | None, campo: str) -> str:
    return _em_sao_paulo(valor, campo).strftime("%d/%m/%Y às %H:%M")


def _formatar_data_extenso(valor: datetime | None, campo: str) -> str:
    data = _em_sao_paulo(valor, campo)
    return f"{data.day} de {MESES[data.month - 1]} de {data.year}"


def _logo_data_uri() -> str:
    try:
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    except OSError as exc:
        raise TermoEquipamentoError("Logotipo do termo de equipamentos não encontrado.") from exc
    return f"data:image/png;base64,{encoded}"


def _texto_obrigatorio(objeto, atributo: str, rotulo: str) -> str:
    valor = getattr(objeto, atributo, None)
    if not isinstance(valor, str) or not valor.strip():
        raise TermoEquipamentoError(f"{rotulo} não está registrado na solicitação.")
    return valor.strip()


def _validar_versao_solicitacao(solicitacao: SolicitacaoEquipamento) -> None:
    versao = getattr(solicitacao, "termo_versao", None)
    if versao is None:
        return

    hash_atual = obter_hash_template(versao.codigo)
    if versao.conteudo_hash != hash_atual or versao.clausulas != obter_clausulas_termo(versao.codigo):
        raise TermoEquipamentoError(
            "O template versionado foi alterado sem atualização da versão do termo."
        )


def _itens_snapshot(solicitacao: SolicitacaoEquipamento) -> list[dict[str, str | None]]:
    itens_ativos = [
        item
        for item in (getattr(solicitacao, "itens", None) or [])
        if getattr(item, "status_item", None) != "removido"
    ]
    itens_ativos.sort(key=lambda item: getattr(item, "id", 0) or 0)

    if not itens_ativos:
        raise TermoEquipamentoError("A solicitação não possui itens entregues para emissão do termo.")

    itens = []
    for item in itens_ativos:
        tipo = _texto_obrigatorio(item, "tipo_snapshot", "Tipo do equipamento")
        marca_modelo = _texto_obrigatorio(item, "marca_modelo_snapshot", "Marca/modelo do equipamento")
        estado = _texto_obrigatorio(
            item,
            "estado_conservacao_snapshot",
            "Estado de conservação do equipamento",
        )
        itens.append(
            {
                "tipo_codigo": tipo,
                "tipo": TIPOS_LABEL.get(tipo, tipo.replace("_", " ").title()),
                "numero_patrimonio": getattr(item, "numero_patrimonio_snapshot", None),
                "numero_serie": getattr(item, "numero_serie_snapshot", None),
                "marca_modelo": marca_modelo,
                "estado_conservacao": estado,
                "observacoes": getattr(item, "observacoes_snapshot", None),
            }
        )
    return itens


def _contexto_termo(
    solicitacao: SolicitacaoEquipamento,
    cpf_completo: str,
    versao_codigo: str = TERMO_VERSAO_CODIGO,
) -> dict:
    solicitacao_id = getattr(solicitacao, "id", None)
    if not isinstance(solicitacao_id, int) or solicitacao_id <= 0:
        raise TermoEquipamentoError("Solicitação inválida para geração do termo.")

    try:
        cpf = formatar_cpf(validar_cpf(cpf_completo))
    except ValueError as exc:
        raise TermoEquipamentoError("CPF do colaborador inválido para geração do termo.") from exc

    if not getattr(solicitacao, "aceite_declaracao", False):
        raise TermoEquipamentoError("O aceite do termo ainda não foi confirmado.")

    _validar_versao_solicitacao(solicitacao)
    itens = _itens_snapshot(solicitacao)
    tipos_presentes = {item["tipo_codigo"] for item in itens}

    nome = _texto_obrigatorio(solicitacao, "nome_colaborador_snapshot", "Nome do colaborador")
    cargo = _texto_obrigatorio(solicitacao, "cargo_snapshot", "Cargo do colaborador")
    departamento = _texto_obrigatorio(
        solicitacao,
        "departamento_snapshot",
        "Departamento do colaborador",
    )
    responsavel_nome = _texto_obrigatorio(
        solicitacao,
        "responsavel_entrega_nome",
        "Responsável pela entrega",
    )
    responsavel_cargo = _texto_obrigatorio(
        solicitacao,
        "responsavel_entrega_cargo",
        "Cargo do responsável pela entrega",
    )
    local_entrega = _texto_obrigatorio(solicitacao, "local_entrega", "Local da entrega")
    local_aceite = _texto_obrigatorio(solicitacao, "local_aceite", "Local do aceite")

    return {
        "identificador": f"AUT-EQP-{solicitacao_id:06d}",
        "versao_codigo": versao_codigo,
        # A emissão é o aceite oficial do backend, não o relógio da regeneração.
        "emitido_em": _formatar_data_hora(solicitacao.aceito_em, "Data do aceite"),
        "logo_data_uri": _logo_data_uri(),
        "colaborador": {
            "nome": nome,
            "cpf": cpf,
            "cargo": cargo,
            "departamento": departamento,
        },
        "data_solicitacao": _formatar_data(solicitacao.criado_em, "Data da solicitação"),
        "data_entrega": _formatar_data(solicitacao.entregue_em, "Data da entrega"),
        "local_aceite": local_aceite,
        "data_aceite_extenso": _formatar_data_extenso(solicitacao.aceito_em, "Data do aceite"),
        "entrega": {
            "responsavel_nome": responsavel_nome,
            "responsavel_cargo": responsavel_cargo,
            "local": local_entrega,
        },
        "aceite": {
            "data_hora": _formatar_data_hora(solicitacao.aceito_em, "Data do aceite"),
            "ip": getattr(solicitacao, "aceite_ip", None),
            "request_id": getattr(solicitacao, "aceite_request_id", None),
        },
        "tipos_catalogo": [
            {
                "codigo": codigo,
                "nome": nome_tipo,
                "selecionado": codigo in tipos_presentes,
            }
            for codigo, nome_tipo in TIPOS_LABEL.items()
        ],
        "itens": itens,
        "observacoes_solicitacao": getattr(solicitacao, "observacoes", None),
    }


def renderizar_termo_html(solicitacao: SolicitacaoEquipamento, cpf_completo: str) -> str:
    versao_codigo = (
        solicitacao.termo_versao.codigo
        if getattr(solicitacao, "termo_versao", None)
        else TERMO_VERSAO_CODIGO
    )
    try:
        template = _JINJA.from_string(obter_conteudo_template(versao_codigo))
        return template.render(**_contexto_termo(solicitacao, cpf_completo, versao_codigo))
    except TermoEquipamentoError:
        raise
    except Exception as exc:
        raise TermoEquipamentoError("Não foi possível renderizar o termo de equipamentos.") from exc


def gerar_termo_pdf(solicitacao: SolicitacaoEquipamento, cpf_completo: str) -> TermoGerado:
    versao_codigo = (
        solicitacao.termo_versao.codigo
        if getattr(solicitacao, "termo_versao", None)
        else TERMO_VERSAO_CODIGO
    )
    html = renderizar_termo_html(solicitacao, cpf_completo)
    try:
        # Import tardio: metadados/versionamento continuam acessíveis em tarefas de migração
        # mesmo antes de as bibliotecas nativas do renderizador estarem carregadas.
        from weasyprint import HTML

        pdf_bytes = HTML(string=html).write_pdf()
    except Exception as exc:
        raise TermoEquipamentoError("Não foi possível gerar o PDF do termo de equipamentos.") from exc

    if not pdf_bytes.startswith(b"%PDF-"):
        raise TermoEquipamentoError("O renderizador retornou um documento PDF inválido.")

    nome_colaborador = _texto_obrigatorio(
        solicitacao,
        "nome_colaborador_snapshot",
        "Nome do colaborador",
    )
    return TermoGerado(
        versao_codigo=versao_codigo,
        conteudo_hash=obter_hash_template(versao_codigo),
        html=html,
        pdf_bytes=pdf_bytes,
        pdf_hash=hashlib.sha256(pdf_bytes).hexdigest(),
        nome_arquivo=montar_nome_arquivo_termo(
            nome_colaborador,
            solicitacao.id,
            versao_codigo,
        ),
    )


def gerar_pdf_snapshot(solicitacao: SolicitacaoEquipamento) -> TermoGerado:
    html = descriptografar_dado_sensivel(solicitacao.termo_html_snapshot_criptografado)
    if not html or not solicitacao.termo_versao:
        raise TermoEquipamentoError("Snapshot histórico do termo não está disponível.")
    try:
        from weasyprint import HTML

        pdf_bytes = HTML(string=html).write_pdf()
    except Exception as exc:
        raise TermoEquipamentoError("Não foi possível regenerar o PDF histórico.") from exc
    if not pdf_bytes.startswith(b"%PDF-"):
        raise TermoEquipamentoError("O renderizador retornou um documento PDF inválido.")
    return TermoGerado(
        versao_codigo=solicitacao.termo_versao.codigo,
        conteudo_hash=solicitacao.termo_versao.conteudo_hash,
        html=html,
        pdf_bytes=pdf_bytes,
        pdf_hash=hashlib.sha256(pdf_bytes).hexdigest(),
        nome_arquivo=montar_nome_arquivo_termo(
            solicitacao.nome_colaborador_snapshot,
            solicitacao.id,
            solicitacao.termo_versao.codigo,
        ),
    )


def _documento_existente_valido(db: Session, solicitacao: SolicitacaoEquipamento) -> Documento | None:
    if not solicitacao.documento_id:
        return None
    documento = db.query(Documento).filter(Documento.id == solicitacao.documento_id).first()
    if not documento or documento.user_id != solicitacao.user_id or documento.tipo != "termo_equipamentos":
        return None
    try:
        caminho_documento(documento)
    except HTTPException:
        return None
    return documento


def garantir_versao_termo(db: Session) -> TermoEquipamentoVersao:
    """Garante o registro imutável da versão atual sem encerrar a transação do chamador."""
    metadados = obter_metadados_versao()
    dialect = getattr(getattr(db, "bind", None), "dialect", None)
    if getattr(dialect, "name", None) == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(:chave)"), {"chave": 4_000_001})
    versao = patrimonios_repository.obter_versao_termo_por_codigo(db, TERMO_VERSAO_CODIGO)
    if versao is None:
        versao = TermoEquipamentoVersao(
            codigo=metadados["codigo"],
            vigente_desde=datetime.now(UTC),
            conteudo_hash=metadados["conteudo_hash"],
            clausulas=metadados["clausulas"],
            ativo=True,
        )
        db.add(versao)
        db.flush()

    if versao.conteudo_hash != metadados["conteudo_hash"] or versao.clausulas != metadados["clausulas"]:
        raise TermoEquipamentoError(
            "A versão atual do termo foi alterada sem incremento do código de versão."
        )
    return versao


def _obter_ou_criar_versao(db: Session, solicitacao: SolicitacaoEquipamento) -> TermoEquipamentoVersao:
    versao = solicitacao.termo_versao
    if versao is None:
        versao = garantir_versao_termo(db)
    elif (
        versao.conteudo_hash != obter_hash_template(versao.codigo)
        or versao.clausulas != obter_clausulas_termo(versao.codigo)
    ):
        raise TermoEquipamentoError(
            "A versão histórica do termo não corresponde ao template versionado disponível."
        )
    solicitacao.termo_versao = versao
    return versao


def _registrar_falha_geracao(
    db: Session,
    solicitacao_id: int,
    current_user: User,
) -> None:
    try:
        db.rollback()
        solicitacao = patrimonios_repository.obter_solicitacao(db, solicitacao_id)
        if solicitacao is None:
            return
        solicitacao.documento_status = "falha"
        solicitacao.documento_erro = (
            "Falha técnica ao gerar o termo. A operação pode ser repetida por um administrador."
        )
        log = log_service.construir_log(
            current_user,
            acao="TERMO_EQUIPAMENTOS_FALHA",
            detalhes=f"Falha técnica na geração do termo da solicitação #{solicitacao_id}",
        )
        if log is not None:
            db.add(log)
        db.commit()
    except Exception:
        db.rollback()


def gerar_termo_definitivo(
    db: Session,
    solicitacao_id: int,
    current_user: User,
    regenerar: bool = False,
) -> Documento:
    """Gera e integra o termo definitivo ao módulo de documentos em uma única linha histórica."""
    solicitacao = patrimonios_repository.obter_solicitacao(db, solicitacao_id, bloquear=True)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="Solicitação de equipamento não encontrada")
    if current_user.role != "admin" and solicitacao.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    if regenerar and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem regenerar o termo")

    documento_existente = _documento_existente_valido(db, solicitacao)
    if documento_existente is not None and not regenerar:
        return documento_existente

    if not solicitacao.aceite_declaracao or not solicitacao.aceito_em:
        raise HTTPException(status_code=400, detail="O termo ainda não foi aceito pelo colaborador")
    if not solicitacao.entregue_em:
        raise HTTPException(status_code=400, detail="A entrega deve ser registrada antes da emissão do termo")

    arquivo = None
    commit_concluido = False
    try:
        if not (
            regenerar
            and solicitacao.termo_html_snapshot_criptografado
            and solicitacao.termo_versao
        ):
            _obter_ou_criar_versao(db, solicitacao)
        cpf_completo = descriptografar_dado_sensivel(solicitacao.cpf_snapshot_criptografado)
        if not cpf_completo:
            raise TermoEquipamentoError("CPF histórico do colaborador não está disponível.")

        termo = (
            gerar_pdf_snapshot(solicitacao)
            if regenerar and solicitacao.termo_html_snapshot_criptografado
            else gerar_termo_pdf(solicitacao, cpf_completo)
        )
        arquivo = salvar_termo_pdf(
            termo.pdf_bytes,
            solicitacao.nome_colaborador_snapshot,
            solicitacao.id,
            termo.versao_codigo,
        )

        documento = documento_existente
        if documento is None and solicitacao.documento_id:
            documento = db.query(Documento).filter(Documento.id == solicitacao.documento_id).first()

        criado_por_id = solicitacao.entregue_por_id or solicitacao.aprovado_por_id or current_user.id
        if documento is None:
            documento = Documento(
                user_id=solicitacao.user_id,
                tipo="termo_equipamentos",
                nome_arquivo=arquivo.nome_arquivo,
                mime_type="application/pdf",
                caminho_arquivo=arquivo.caminho_relativo,
                caminho_enviado=None,
                tamanho=arquivo.tamanho,
                criado_por_id=criado_por_id,
                destino_tipo="usuario",
                destinatario_id=solicitacao.user_id,
            )
            db.add(documento)
            db.flush()
        else:
            if documento.user_id != solicitacao.user_id:
                raise TermoEquipamentoError("Documento histórico associado a outro colaborador.")
            documento.tipo = "termo_equipamentos"
            documento.nome_arquivo = arquivo.nome_arquivo
            documento.mime_type = "application/pdf"
            documento.caminho_arquivo = arquivo.caminho_relativo
            documento.caminho_enviado = None
            documento.tamanho = arquivo.tamanho
            documento.destino_tipo = "usuario"
            documento.destinatario_id = solicitacao.user_id

        solicitacao.termo_versao_id = solicitacao.termo_versao.id
        if not solicitacao.termo_html_snapshot_criptografado:
            solicitacao.termo_html_snapshot_criptografado = criptografar_dado_sensivel(termo.html)
        solicitacao.documento_id = documento.id
        solicitacao.documento_hash = termo.pdf_hash
        solicitacao.documento_status = "gerado"
        solicitacao.documento_erro = None
        solicitacao.status = "entregue"

        acao = "TERMO_EQUIPAMENTOS_REGENERADO" if regenerar else "TERMO_EQUIPAMENTOS_GERADO"
        log = log_service.construir_log(
            current_user,
            acao=acao,
            detalhes=(
                f"Termo {termo.versao_codigo} da solicitação #{solicitacao.id} "
                f"associado ao documento #{documento.id}"
            ),
        )
        if log is not None:
            db.add(log)
        db.commit()
        commit_concluido = True
        confirmar_termo_pdf(arquivo)
        db.refresh(documento)
        return documento
    except HTTPException:
        if arquivo is not None and not commit_concluido:
            reverter_termo_pdf(arquivo)
        raise
    except Exception as exc:
        if arquivo is not None and not commit_concluido:
            reverter_termo_pdf(arquivo)
        if not commit_concluido:
            _registrar_falha_geracao(db, solicitacao_id, current_user)
        if isinstance(exc, TermoEquipamentoError):
            raise
        raise TermoEquipamentoError("Não foi possível concluir a geração do termo.") from exc
