import base64
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import envios_repository

router = APIRouter(tags=["Rastreio"])

# PNG 1x1 transparente, gerado uma única vez - nunca lido de disco por request.
_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


@router.get("/track/{token}.png")
def rastrear_abertura(token: str, db: Session = Depends(get_db)) -> Response:
    """Pixel de rastreio de leitura. Rota pública, sem autenticação, por natureza.

    Marca `lido_em` na primeira vez que o token é visto. Sempre responde 200 com a mesma
    imagem, exista o token ou não - o comportamento nunca deve vazar se um token é válido.

    Esta é uma confirmação de leitura PROBABILÍSTICA: o proxy de imagens do Gmail pode
    disparar (ou deixar de disparar) esta request independentemente de o destinatário ter
    de fato aberto o e-mail, então `lido_em` é um indício, nunca uma garantia.
    """
    envio = envios_repository.obter_envio_por_token(db, token)
    if envio is not None and envio.lido_em is None:
        envio.lido_em = datetime.now(UTC)
        db.commit()

    return Response(content=_PIXEL_PNG, media_type="image/png")
