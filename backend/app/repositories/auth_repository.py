from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.departamento import Departamento
from app.models.user import User


def obter_usuario_por_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(User.email) == email.lower(), User.ativo.is_(True)).first()


def obter_departamento_por_id(db: Session, departamento_id: int) -> Departamento | None:
    return db.query(Departamento).filter(Departamento.id == departamento_id).first()
