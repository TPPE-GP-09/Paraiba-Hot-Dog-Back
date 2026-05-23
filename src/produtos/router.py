from fastapi import APIRouter, Depends, Query, status
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

router = APIRouter()

@router.get(
    "/categorias",
    response_model=list[CategoriaRead],
)
def listar_categorias(
    db: Session = Depends(get_db),
) -> list[CategoriaRead]:
    return repository.listar_categorias(db)


@router.post(
    "/categorias",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
) -> CategoriaRead:
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
    return repository.atualizar_categoria(db, categoria_id, data)


@router.delete(
    "/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
) -> None:
    repository.excluir_categoria(db, categoria_id)

@router.get(
    "/subcategorias",
    response_model=list[SubcategoriaRead],
)
def listar_subcategorias(
    db: Session = Depends(get_db),
) -> list[SubcategoriaRead]:
    return repository.listar_subcategorias(db)


@router.post(
    "/subcategorias",
    response_model=SubcategoriaRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_subcategoria(
    data: SubcategoriaCreate,
    db: Session = Depends(get_db),
) -> SubcategoriaRead:
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
    return repository.atualizar_subcategoria(db, subcategoria_id, data)


@router.delete(
    "/subcategorias/{subcategoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_subcategoria(
    subcategoria_id: int,
    db: Session = Depends(get_db),
) -> None:
    repository.excluir_subcategoria(db, subcategoria_id)


@router.get(
    "/variacoes",
    response_model=list[ProdutoVariacaoRead],
)
def listar_variacoes(
    db: Session = Depends(get_db),
) -> list[ProdutoVariacaoRead]:
    return repository.listar_variacoes(db)


@router.post(
    "/variacoes",
    response_model=ProdutoVariacaoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_variacao(
    data: ProdutoVariacaoCreate,
    db: Session = Depends(get_db),
) -> ProdutoVariacaoRead:
    return repository.criar_variacao(db, data)


@router.patch(
    "/variacoes/{variacao_id}",
    response_model=ProdutoVariacaoRead,
)
def atualizar_variacao(
    variacao_id: int,
    data: ProdutoVariacaoUpdate,
    db: Session = Depends(get_db),
) -> ProdutoVariacaoRead:
    return repository.atualizar_variacao(
        db,
        variacao_id,
        data,
    )


@router.delete(
    "/variacoes/{variacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_variacao(
    variacao_id: int,
    db: Session = Depends(get_db),
) -> None:
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
    return repository.listar_adicionais(db)


@router.post(
    "/adicionais",
    response_model=ProdutoAdicionalRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_adicional(
    data: ProdutoAdicionalCreate,
    db: Session = Depends(get_db),
) -> ProdutoAdicionalRead:
    return repository.criar_adicional(db, data)


@router.patch(
    "/adicionais/{adicional_id}",
    response_model=ProdutoAdicionalRead,
)
def atualizar_adicional(
    adicional_id: int,
    data: ProdutoAdicionalUpdate,
    db: Session = Depends(get_db),
) -> ProdutoAdicionalRead:
    return repository.atualizar_adicional(
        db,
        adicional_id,
        data,
    )


@router.delete(
    "/adicionais/{adicional_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_adicional(
    adicional_id: int,
    db: Session = Depends(get_db),
) -> None:
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
    return repository.listar_produtos(db, skip, limit, unidade_id)


@router.get(
    "/{produto_id}",
    response_model=ProdutoRead,
)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    return repository.obter_produto(db, produto_id)


@router.post(
    "/",
    response_model=ProdutoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    return repository.criar_produto(db, produto)


@router.patch(
    "/{produto_id}",
    response_model=ProdutoRead,
)
def atualizar_produto(
    produto_id: int,
    data: ProdutoUpdate,
    db: Session = Depends(get_db),
) -> ProdutoRead:
    return repository.atualizar_produto(
        db,
        produto_id,
        data,
    )


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> None:
    repository.excluir_produto(db, produto_id)
