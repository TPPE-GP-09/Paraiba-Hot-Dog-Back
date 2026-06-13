from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.produtos import repository
from src.produtos.schema import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaUpdate,
    ProdutoCreate,
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
UPLOAD_DIR = Path("uploads/produtos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def salvar_imagem_upload(file: UploadFile) -> str:
    """Salva uma imagem de produto enviada via multipart e retorna a URL publica."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo de imagem valido.",
        )

    extensao = Path(file.filename or "").suffix.lower()
    nome_arquivo = f"{uuid4()}{extensao}"
    caminho = UPLOAD_DIR / nome_arquivo

    with caminho.open("wb") as buffer:
        buffer.write(await file.read())

    return f"/uploads/produtos/{nome_arquivo}"

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
)
async def criar_produto(
    nome: str = Form(...),
    subcategoria_id: int = Form(...),
    descricao: str | None = Form(None),
    ativo: bool = Form(True),
    pontos_fidelidade_por_unidade: int = Form(0),
    disponivel_todas_unidades: bool = Form(True),
    unidade_ids: list[int] | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ProdutoRead:
    """Cria um novo produto e vincula a imagem enviada."""
    imagem_url = await salvar_imagem_upload(file)
    produto = ProdutoCreate(
        nome=nome,
        descricao=descricao,
        imagem_url=imagem_url,
        ativo=ativo,
        pontos_fidelidade_por_unidade=pontos_fidelidade_por_unidade,
        disponivel_todas_unidades=disponivel_todas_unidades,
        subcategoria_id=subcategoria_id,
        unidade_ids=unidade_ids or [],
    )
    return repository.criar_produto(db, produto)


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
