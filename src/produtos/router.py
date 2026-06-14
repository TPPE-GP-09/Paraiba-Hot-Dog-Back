from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from src.database import get_db
from src.produtos import repository
from src.produtos.schema import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
    ProdutoCreate,
    ProdutoMultipartCreate,
    ProdutoRead,
    ProdutoUpdate,
    ProdutoVariacaoCreate,
    ProdutoVariacaoRead,
    ProdutoVariacaoUpdate,
    SubcategoriaCreate,
    SubcategoriaRead,
    SubcategoriaUpdate,
    ProdutoAdicionalCreate,
    ProdutoAdicionalRead,
    ProdutoAdicionalUpdate,
)
from src.security import get_current_user

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "produtos"
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


CRIAR_PRODUTO_REQUEST_BODY = _multipart_request_body(ProdutoMultipartCreate)


async def salvar_imagem_upload(imagem: UploadFile) -> str:
    """Salva uma imagem de produto enviada via multipart e retorna a URL publica."""
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

    return f"/uploads/produtos/{nome_arquivo}"


def _erro_validacao(exc: ValidationError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())


def _is_upload_file(value: object) -> bool:
    return hasattr(value, "read") and hasattr(value, "content_type")


def _form_bool(value: object, default: bool) -> object:
    if value is None:
        return default
    if isinstance(value, str):
        return value.lower() in {"1", "true", "on", "yes"}
    return value


async def _produto_data_from_request(request: Request) -> ProdutoCreate:
    content_type = request.headers.get("content-type", "")
    try:
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            imagem = form.get("imagem")
            imagem_url = await salvar_imagem_upload(imagem) if _is_upload_file(imagem) else form.get("imagem_url")
            return ProdutoCreate.model_validate(
                {
                    "nome": form.get("nome"),
                    "descricao": form.get("descricao"),
                    "imagem_url": imagem_url,
                    "ativo": _form_bool(form.get("ativo"), True),
                    "pontos_fidelidade_por_unidade": form.get("pontos_fidelidade_por_unidade", 0),
                    "disponivel_todas_unidades": _form_bool(form.get("disponivel_todas_unidades"), True),
                    "subcategoria_id": form.get("subcategoria_id"),
                    "unidade_ids": form.getlist("unidade_ids"),
                }
            )
        return ProdutoCreate.model_validate(await request.json())
    except ValidationError as exc:
        raise _erro_validacao(exc) from exc


@router.get(
    "/categorias",
    response_model=list[CategoriaRead],
)
def listar_categorias(
    db: Session = Depends(get_db),
) -> list[CategoriaRead]:
    """Lista todas as categorias de produto."""
    return repository.listar_categorias(db)


@router.post(
    "/categorias",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
) -> CategoriaRead:
    """Cria uma nova categoria de produto. Requer autenticacao."""
    return repository.criar_categoria(db, data)


@router.patch(
    "/categorias/{categoria_id}",
    response_model=CategoriaRead,
)
def atualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    db: Session = Depends(get_db),
) -> CategoriaRead:
    """Atualiza parcialmente uma categoria de produto existente."""
    return repository.atualizar_categoria(db, categoria_id, data)


@router.delete(
    "/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove uma categoria de produto pelo ID."""
    repository.excluir_categoria(db, categoria_id)

@router.get(
    "/subcategorias",
    response_model=list[SubcategoriaRead],
)
def listar_subcategorias(
    db: Session = Depends(get_db),
) -> list[SubcategoriaRead]:
    """Lista todas as subcategorias de produto."""
    return repository.listar_subcategorias(db)


@router.post(
    "/subcategorias",
    response_model=SubcategoriaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_subcategoria(
    data: SubcategoriaCreate,
    db: Session = Depends(get_db),
) -> SubcategoriaRead:
    """Cria uma nova subcategoria vinculada a uma categoria existente. Requer autenticacao."""
    return repository.criar_subcategoria(db, data)


@router.patch(
    "/subcategorias/{subcategoria_id}",
    response_model=SubcategoriaRead,
)
def atualizar_subcategoria(
    subcategoria_id: int,
    data: SubcategoriaUpdate,
    db: Session = Depends(get_db),
) -> SubcategoriaRead:
    """Atualiza parcialmente uma subcategoria existente."""
    return repository.atualizar_subcategoria(db, subcategoria_id, data)


@router.delete(
    "/subcategorias/{subcategoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_subcategoria(
    subcategoria_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove uma subcategoria de produto pelo ID."""
    repository.excluir_subcategoria(db, subcategoria_id)


@router.get(
    "/variacoes",
    response_model=list[ProdutoVariacaoRead],
)
def listar_variacoes(
    db: Session = Depends(get_db),
) -> list[ProdutoVariacaoRead]:
    """Lista todas as variacoes de produto."""
    return repository.listar_variacoes(db)


@router.post(
    "/variacoes",
    response_model=ProdutoVariacaoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_variacao(
    data: ProdutoVariacaoCreate,
    db: Session = Depends(get_db),
) -> ProdutoVariacaoRead:
    """Cria uma nova variacao para um produto existente. Requer autenticacao."""
    return repository.criar_variacao(db, data)


@router.patch(
    "/variacoes/{variacao_id}",
    response_model=ProdutoVariacaoRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_variacao(
    variacao_id: int,
    data: ProdutoVariacaoUpdate,
    db: Session = Depends(get_db),
) -> ProdutoVariacaoRead:
    """Atualiza parcialmente uma variacao de produto existente. Requer autenticacao."""
    return repository.atualizar_variacao(
        db,
        variacao_id,
        data,
    )


@router.delete(
    "/variacoes/{variacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_variacao(
    variacao_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove uma variacao de produto pelo ID. Requer autenticacao."""
    repository.excluir_variacao(
        db,
        variacao_id,
    )


@router.get(
    "/adicionais",
    response_model=list[ProdutoAdicionalRead],
)
def listar_adicionais(
    db: Session = Depends(get_db),
) -> list[ProdutoAdicionalRead]:
    """Lista todos os adicionais de produto."""
    return repository.listar_adicionais(db)


@router.post(
    "/adicionais",
    response_model=ProdutoAdicionalRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_adicional(
    data: ProdutoAdicionalCreate,
    db: Session = Depends(get_db),
) -> ProdutoAdicionalRead:
    """Cria um novo adicional vinculado a um produto. Requer autenticacao."""
    return repository.criar_adicional(db, data)


@router.patch(
    "/adicionais/{adicional_id}",
    response_model=ProdutoAdicionalRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_adicional(
    adicional_id: int,
    data: ProdutoAdicionalUpdate,
    db: Session = Depends(get_db),
) -> ProdutoAdicionalRead:
    """Atualiza parcialmente um adicional de produto existente. Requer autenticacao."""
    return repository.atualizar_adicional(
        db,
        adicional_id,
        data,
    )


@router.delete(
    "/adicionais/{adicional_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_adicional(
    adicional_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove um adicional de produto pelo ID. Requer autenticacao."""
    repository.excluir_adicional(
        db,
        adicional_id,
    )


@router.get(
    "/",
    response_model=list[ProdutoRead],
)
def listar_produtos(
    skip: int = 0,
    limit: int = Query(100, le=100),
    unidade_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
) -> list[ProdutoRead]:
    """Lista produtos com paginacao e filtro opcional por unidade."""
    return repository.listar_produtos(db, skip, limit, unidade_id)


@router.get(
    "/{produto_id}",
    response_model=ProdutoRead,
)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    """Retorna os detalhes de um produto pelo ID."""
    return repository.obter_produto(db, produto_id)


@router.post(
    "/",
    response_model=ProdutoRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
    openapi_extra={"requestBody": CRIAR_PRODUTO_REQUEST_BODY},
)
async def criar_produto(
    request: Request,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    """Cria um produto via JSON ou multipart com imagem."""
    return repository.criar_produto(db, await _produto_data_from_request(request))


@router.patch(
    "/{produto_id}",
    response_model=ProdutoRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_produto(
    produto_id: int,
    data: ProdutoUpdate,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    """Atualiza parcialmente um produto existente. Requer autenticacao."""
    return repository.atualizar_produto(
        db,
        produto_id,
        data,
    )


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Remove um produto pelo ID. Requer autenticacao."""
    repository.excluir_produto(db, produto_id)
