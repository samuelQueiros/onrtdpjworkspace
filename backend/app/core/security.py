import bcrypt
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
_login_attempts: dict[str, deque[float]] = defaultdict(deque)
_login_lock = threading.Lock()
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_MAX_ATTEMPTS = 5


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def criar_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_limite_login(chave: str) -> None:
    agora = time.monotonic()
    with _login_lock:
        expiradas = []
        for existente, tentativas_existentes in _login_attempts.items():
            while tentativas_existentes and agora - tentativas_existentes[0] > LOGIN_WINDOW_SECONDS:
                tentativas_existentes.popleft()
            if not tentativas_existentes:
                expiradas.append(existente)
        for existente in expiradas:
            _login_attempts.pop(existente, None)
        tentativas = _login_attempts[chave]
        if len(tentativas) >= LOGIN_MAX_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente mais tarde.")


def registrar_falha_login(chave: str) -> None:
    with _login_lock:
        _login_attempts[chave].append(time.monotonic())


def limpar_falhas_login(chave: str) -> None:
    with _login_lock:
        _login_attempts.pop(chave, None)


def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        auth_token = token or request.cookies.get("access_token")
        if not auth_token:
            raise credentials_exception
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_version = payload.get("token_version")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id), User.ativo.is_(True)).first()
    if user is None:
        raise credentials_exception
    if token_version != user.token_version:
        raise credentials_exception
    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user
