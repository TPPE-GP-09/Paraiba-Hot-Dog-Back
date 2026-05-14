from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.permissoes.model import Permissao
from src.usuarios.model import Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate


def _resolver_permissoes(db: Session, ids: list[int]) -> list[Permissao]:
    permissoes = db.query(Permissao).filter(Permissao.id.in_(ids)).all()
    if len(permissoes) != len(ids):
        raise HTTPException(status_code=404, detail="Uma ou mais permissoes nao encontradas")
    return permissoes


def create_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    permissoes = _resolver_permissoes(db, data.permissao_ids)
    db_usuario = Usuario(**data.model_dump(exclude={"permissao_ids"}))
    db_usuario.permissoes = permissoes
    db.add(db_usuario)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        detail = "Email ja cadastrado" if "email" in str(e.orig) else "Violacao de integridade"
        raise HTTPException(status_code=409, detail=detail)
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
    update_data = data.model_dump(exclude_unset=True)
    if "permissao_ids" in update_data:
        usuario.permissoes = _resolver_permissoes(db, update_data.pop("permissao_ids"))
    for field, value in update_data.items():
        setattr(usuario, field, value)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        detail = "Email ja cadastrado" if "email" in str(e.orig) else "Violacao de integridade"
        raise HTTPException(status_code=409, detail=detail)
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario_id: int) -> None:
    usuario = get_usuario(db, usuario_id)
    db.delete(usuario)
    db.commit()
