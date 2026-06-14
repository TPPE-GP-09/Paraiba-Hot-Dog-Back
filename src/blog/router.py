from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from src.blog import repository
from src.blog.model import TipoNoticiaPromocao
from src.blog.schema import BlogCreate, BlogRead, BlogUpdate
from src.database import get_db
from src.security import get_current_user

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "blog"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def salvar_imagem_upload(imagem: UploadFile) -> str:
    """Salva uma imagem enviada via multipart e retorna a URL publica."""
    if not imagem.content_type or not imagem.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo de imagem valido.",
        )

    extensao = Path(imagem.filename or "").suffix.lower()
    nome_arquivo = f"{uuid4()}{extensao}"
    caminho = UPLOAD_DIR / nome_arquivo

    with caminho.open("wb") as buffer:
        buffer.write(await imagem.read())

    return f"/uploads/blog/{nome_arquivo}"


@router.get("/", response_model=list[BlogRead])
def listar_posts(tipo: str | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista as postagens do blog com paginacao e filtro opcional por tipo."""
    return repository.listar_posts(db, tipo, skip, limit)


@router.post(
    "/",
    response_model=BlogRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def criar_post(
    titulo: str = Form(...),
    tipo: TipoNoticiaPromocao = Form(...),
    data: date = Form(...),
    descricao: str | None = Form(None),
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Cria uma postagem do blog e vincula a imagem enviada."""
    imagem_url = await salvar_imagem_upload(imagem)
    post_data = BlogCreate(
        titulo=titulo,
        imagem_url=imagem_url,
        descricao=descricao,
        tipo=tipo,
        data=data,
    )
    return repository.criar_post(db, post_data)


@router.get("/{post_id}", response_model=BlogRead)
def obter_post(post_id: int, db: Session = Depends(get_db)):
    """Retorna uma postagem pelo ID."""
    return repository.obter_post(db, post_id)


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
