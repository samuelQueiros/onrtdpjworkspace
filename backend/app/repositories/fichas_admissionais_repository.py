from sqlalchemy.orm import Session

from app.models.ficha_admissional import FichaAdmissional


def obter_por_usuario(db: Session, user_id: int) -> FichaAdmissional | None:
    return db.query(FichaAdmissional).filter(FichaAdmissional.user_id == user_id).first()


def salvar(db: Session, ficha: FichaAdmissional, commit: bool = True) -> FichaAdmissional:
    db.add(ficha)
    if commit:
        db.commit()
        db.refresh(ficha)
    return ficha
