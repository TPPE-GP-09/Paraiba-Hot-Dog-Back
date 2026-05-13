from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.model.usuario import Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate


def create_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    db_usuario = Usuario(**data.model_dump())
    db.add(db_usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    db.refresh(db_usuario)
    return db_usuario


def list_usuarios(db: Session, email: str | None, nome: str | None) -> list[Usuario]:
    query = db.query(Usuario)
    if email:
        query = query.filter(Usuario.email == email)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    return query.order_by(Usuario.id.asc()).all()


def get_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return usuario


def update_usuario(db: Session, usuario_id: int, data: UsuarioUpdate) -> Usuario:
    usuario = get_usuario(db, usuario_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario_id: int) -> None:
    usuario = get_usuario(db, usuario_id)
    db.delete(usuario)
    db.commit()
