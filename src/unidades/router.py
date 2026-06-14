from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from src.database import get_db
from src.unidades import repository
from src.unidades.schema import UnidadeCreate, UnidadeMultipartCreate, UnidadeRead, UnidadeUpdate
from src.security import get_current_user

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "unidades"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _multipart_request_body(schema: type[BaseModel]) -> dict:
    return {
        "content": {
            "multipart/form-data": {
                "schema": schema.model_json_schema(),
            },
        },
        "required": True,
    }


CRIAR_UNIDADE_REQUEST_BODY = _multipart_request_body(UnidadeMultipartCreate)


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


def _erro_validacao(exc: ValidationError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())


def _is_upload_file(value: object) -> bool:
    return hasattr(value, "read") and hasattr(value, "content_type")


async def _unidade_data_from_request(request: Request) -> UnidadeCreate:
    content_type = request.headers.get("content-type", "")
    try:
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            imagem = form.get("imagem")
            imagem_url = await salvar_imagem_upload(imagem) if _is_upload_file(imagem) else form.get("imagem")
            return UnidadeCreate.model_validate(
                {
                    "nome": form.get("nome"),
                    "imagem": imagem_url,
                    "abertura": form.get("abertura"),
                    "fechamento": form.get("fechamento"),
                    "descricao": form.get("descricao"),
                    "endereco": {
                        "cep": form.get("cep"),
                        "logradouro": form.get("logradouro"),
                        "numero": form.get("numero"),
                        "complemento": form.get("complemento"),
                        "bairro": form.get("bairro"),
                        "cidade": form.get("cidade"),
                        "estado": form.get("estado"),
                    },
                }
            )
        return UnidadeCreate.model_validate(await request.json())
    except ValidationError as exc:
        raise _erro_validacao(exc) from exc


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
    openapi_extra={"requestBody": CRIAR_UNIDADE_REQUEST_BODY},
)
async def criar_unidade(
    request: Request,
    db: Session = Depends(get_db),
):
    """Cria uma unidade via JSON ou multipart com imagem."""
    return repository.criar_unidade(db, await _unidade_data_from_request(request))


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
