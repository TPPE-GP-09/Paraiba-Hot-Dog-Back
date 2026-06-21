from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.permissoes.model import Permissao
from src.unidades.model import Unidade
from src.jwt_auth import hash_password
from src.usuarios.model import Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate


def _resolver_permissoes(db: Session, ids: list[int]) -> list[Permissao]:
    """Resolve permissions by IDs, raising 404 if any not found."""
    permissoes = db.query(Permissao).filter(Permissao.id.in_(ids)).all()
    if len(permissoes) != len(ids):
        raise HTTPException(status_code=404, detail="Uma ou mais permissoes nao encontradas")
    return permissoes


def _validar_unidade(db: Session, unidade_id: int | None) -> None:
    """Validate unit exists in database, raising 404 if not found. Ignores None."""
    if unidade_id is None:
        return
    if not db.get(Unidade, unidade_id):
        raise HTTPException(status_code=404, detail="Unidade nao encontrada")


def _tratar_integridade(e: IntegrityError) -> HTTPException:
    """Map database integrity error to appropriate HTTPException."""
    erro = str(e.orig).lower()
    if "email" in erro:
        return HTTPException(status_code=409, detail="Email ja cadastrado")
    if "fk_usuarios_unidade_id" in erro or "usuarios_unidade_id_fkey" in erro:
        return HTTPException(status_code=404, detail="Unidade nao encontrada")
    return HTTPException(status_code=409, detail="Violacao de integridade")


def create_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    """Create a new user in database with hashed password."""
    permissoes = _resolver_permissoes(db, data.permissao_ids)
    _validar_unidade(db, data.unidade_id)

    db_usuario = Usuario(
        **data.model_dump(exclude={"permissao_ids", "senha"}),
        senha_hash=hash_password(data.senha),
    )
    db_usuario.permissoes = permissoes
    db.add(db_usuario)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise _tratar_integridade(e) from e
    db.refresh(db_usuario)
    return db_usuario


def list_usuarios(db: Session, email: str | None, nome: str | None) -> list[Usuario]:
    """List users with optional email and name filters, ordered by ID."""
    query = db.query(Usuario)
    if email:
        query = query.filter(Usuario.email == email)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))
    return query.order_by(Usuario.id.asc()).all()


def get_usuario(db: Session, usuario_id: int) -> Usuario:
    """Get a user by ID or raise 404 if not found."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return usuario


def update_usuario(db: Session, usuario_id: int, data: UsuarioUpdate) -> Usuario:
    """Update user fields with optional password update."""
    usuario = get_usuario(db, usuario_id)
    update_data = data.model_dump(exclude_unset=True)

    if "unidade_id" in update_data:
        _validar_unidade(db, update_data["unidade_id"])
    if "permissao_ids" in update_data:
        usuario.permissoes = _resolver_permissoes(db, update_data.pop("permissao_ids"))

    senha = update_data.pop("senha", None)
    if senha is not None:
        update_data["senha_hash"] = hash_password(senha)

    for field, value in update_data.items():
        setattr(usuario, field, value)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise _tratar_integridade(e) from e
    db.refresh(usuario)
    return usuario


def delete_usuario(db: Session, usuario_id: int) -> None:
    """Delete a user by ID."""
    usuario = get_usuario(db, usuario_id)
    db.delete(usuario)
    db.commit()
