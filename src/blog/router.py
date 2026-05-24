from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.blog import repository
from src.blog.schema import BlogCreate, BlogRead, BlogUpdate
from src.database import get_db
from src.security import get_current_user

router = APIRouter()


@router.get("/", response_model=list[BlogRead])
def listar_posts(tipo: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista as postagens do blog com paginacao e filtro opcional por tipo."""
    return repository.listar_posts(db, tipo, skip, limit)


@router.get("/{post_id}", response_model=BlogRead)
def obter_post(post_id: int, db: Session = Depends(get_db)):
    """Retorna uma postagem pelo ID."""
    return repository.obter_post(db, post_id)


@router.post(
    "/",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_post(data: BlogCreate, db: Session = Depends(get_db)):
    """Cria uma nova postagem no blog. Requer autenticacao."""
    return repository.criar_post(db, data)


@router.patch(
    "/{post_id}",
    response_model=BlogRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_post(post_id: int, data: BlogUpdate, db: Session = Depends(get_db)):
    """Atualiza parcialmente uma postagem existente. Requer autenticacao."""
    return repository.atualizar_post(db, post_id, data)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_post(post_id: int, db: Session = Depends(get_db)):
    """Remove uma postagem do blog pelo ID. Requer autenticacao."""
    repository.excluir_post(db, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
