from datetime import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.unidades import repository
from src.unidades.schema import EnderecoCreate, UnidadeCreate, UnidadeRead, UnidadeUpdate
from src.security import get_current_user

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "unidades"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def salvar_imagem_upload(imagem: UploadFile) -> str:
    """Salva uma imagem de unidade enviada via multipart e retorna a URL publica."""
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

    return f"/uploads/unidades/{nome_arquivo}"


@router.get("/", response_model=list[UnidadeRead])
def listar_unidades(db: Session = Depends(get_db)):
    """Lista todas as unidades cadastradas."""
    return repository.listar_unidades(db)


@router.get("/{unidade_id}", response_model=UnidadeRead)
def obter_unidade(unidade_id: int, db: Session = Depends(get_db)):
    """Retorna os detalhes de uma unidade pelo ID."""
    return repository.obter_unidade(db, unidade_id)


@router.post(
    "/",
    response_model=UnidadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def criar_unidade(
    nome: str = Form(...),
    abertura: time = Form(...),
    fechamento: time = Form(...),
    cep: str = Form(...),
    logradouro: str = Form(...),
    bairro: str = Form(...),
    cidade: str = Form(...),
    estado: str = Form(...),
    numero: str | None = Form(None),
    complemento: str | None = Form(None),
    descricao: str | None = Form(None),
    imagem: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Cria uma nova unidade e vincula a imagem enviada."""
    imagem_url = await salvar_imagem_upload(imagem)
    data = UnidadeCreate(
        nome=nome,
        imagem=imagem_url,
        abertura=abertura,
        fechamento=fechamento,
        descricao=descricao,
        endereco=EnderecoCreate(
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
        ),
    )
    return repository.criar_unidade(db, data)


@router.patch(
    "/{unidade_id}",
    response_model=UnidadeRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_unidade(unidade_id: int, data: UnidadeUpdate, db: Session = Depends(get_db)):
    """Atualiza parcialmente uma unidade existente. Requer autenticacao."""
    return repository.atualizar_unidade(db, unidade_id, data)


@router.delete(
    "/{unidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_unidade(unidade_id: int, db: Session = Depends(get_db)):
    """Remove uma unidade pelo ID. Requer autenticacao."""
    repository.excluir_unidade(db, unidade_id)
