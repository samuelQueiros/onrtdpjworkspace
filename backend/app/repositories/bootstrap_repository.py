from sqlalchemy.orm import Session

from app.models.log import Log
from app.models.user import User


def obter_admin(db: Session) -> User | None:
    return db.query(User).filter(User.role == "admin").first()


def salvar_admin_com_log(db: Session, admin: User, log: Log) -> User:
    db.add(admin)
    db.flush()
    if log.user_id is None:
        log.user_id = admin.id
    db.add(log)
    db.commit()
    db.refresh(admin)
    return admin
