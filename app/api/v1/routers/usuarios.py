from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def create_usuario(usuario_create: UsuarioCreate, db: Session) -> UsuarioRead:
    db_usuario = Usuario(**usuario_create.model_dump())
    db.add(db_usuario)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    db.refresh(db_usuario)
    return UsuarioRead.model_validate(db_usuario)


@router.post("/", response_model=UsuarioRead)
def create_usuario_endpoint(
    usuario_create: UsuarioCreate,
    db: Session = Depends(get_db),
) -> UsuarioRead:
    return create_usuario(usuario_create, db)


@router.get("/", response_model=list[UsuarioRead])
def list_usuarios(
    email: str | None = Query(default=None),
    nome: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[UsuarioRead]:
    query = db.query(Usuario)
    if email:
        query = query.filter(Usuario.email == email)
    if nome:
        query = query.filter(Usuario.nome.ilike(f"%{nome}%"))

    usuarios = query.order_by(Usuario.id.asc()).all()
    return [UsuarioRead.model_validate(usuario) for usuario in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioRead)
def get_usuario(usuario_id: int, db: Session = Depends(get_db)) -> UsuarioRead:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    return UsuarioRead.model_validate(usuario)


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def update_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
) -> UsuarioRead:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    for field, value in usuario_update.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email ja cadastrado")
    db.refresh(usuario)
    return UsuarioRead.model_validate(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)) -> Response:
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    db.delete(usuario)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
