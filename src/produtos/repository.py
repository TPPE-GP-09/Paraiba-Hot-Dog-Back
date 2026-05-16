from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.produtos.model import (
    Categoria,
    Produto,
    ProdutoVariacao,
    Subcategoria,
    ProdutoAdicional,
)
from src.produtos.schema import (
    CategoriaCreate,
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoVariacaoCreate,
    ProdutoVariacaoUpdate,
    SubcategoriaCreate,
    ProdutoAdicionalCreate,
    ProdutoAdicionalUpdate,
)


def listar_categorias(db: Session) -> list[Categoria]:
    return db.query(Categoria).all()


def criar_categoria(db: Session, data: CategoriaCreate) -> Categoria:
    obj = Categoria(**data.model_dump())

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao criar categoria",
        ) from None

    return obj


def listar_subcategorias(db: Session) -> list[Subcategoria]:
    return db.query(Subcategoria).all()


def criar_subcategoria(db: Session, data: SubcategoriaCreate) -> Subcategoria:
    categoria = db.get(Categoria, data.categoria_id)

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    obj = Subcategoria(**data.model_dump())

    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao criar subcategoria",
        ) from None

    return obj


def listar_produtos(db: Session, skip: int, limit: int) -> list[Produto]:
    return db.query(Produto).offset(skip).limit(limit).all()


def obter_produto(db: Session, produto_id: int) -> Produto:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    return produto


def criar_produto(db: Session, data: ProdutoCreate) -> Produto:
    subcategoria = db.get(Subcategoria, data.subcategoria_id)

    if not subcategoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria nao encontrada",
        )

    db_produto = Produto(**data.model_dump())

    try:
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao criar produto",
        ) from None

    return db_produto


def atualizar_produto(
    db: Session,
    produto_id: int,
    data: ProdutoUpdate,
) -> Produto:
    db_produto = obter_produto(db, produto_id)

    if data.subcategoria_id is not None:
        subcategoria = db.get(Subcategoria, data.subcategoria_id)

        if not subcategoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subcategoria nao encontrada",
            )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_produto, key, value)

    try:
        db.commit()
        db.refresh(db_produto)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao atualizar produto",
        ) from None

    return db_produto


def excluir_produto(db: Session, produto_id: int) -> None:
    db_produto = obter_produto(db, produto_id)

    try:
        db.delete(db_produto)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao excluir produto",
        ) from None


def listar_variacoes(db: Session) -> list[ProdutoVariacao]:
    return db.query(ProdutoVariacao).all()


def obter_variacao(
    db: Session,
    variacao_id: int,
) -> ProdutoVariacao:
    variacao = (
        db.query(ProdutoVariacao)
        .filter(ProdutoVariacao.id == variacao_id)
        .first()
    )

    if variacao is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variacao nao encontrada",
        )

    return variacao


def criar_variacao(
    db: Session,
    data: ProdutoVariacaoCreate,
) -> ProdutoVariacao:
    produto = db.get(Produto, data.produto_id)

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    variacao = ProdutoVariacao(**data.model_dump())

    try:
        db.add(variacao)
        db.commit()
        db.refresh(variacao)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao criar variacao",
        ) from None

    return variacao


def atualizar_variacao(
    db: Session,
    variacao_id: int,
    data: ProdutoVariacaoUpdate,
) -> ProdutoVariacao:
    variacao = obter_variacao(db, variacao_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(variacao, key, value)

    try:
        db.commit()
        db.refresh(variacao)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao atualizar variacao",
        ) from None

    return variacao


def excluir_variacao(
    db: Session,
    variacao_id: int,
) -> None:
    variacao = obter_variacao(db, variacao_id)

    try:
        db.delete(variacao)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao excluir variacao",
        ) from None


def listar_adicionais(
    db: Session,
) -> list[ProdutoAdicional]:
    return db.query(ProdutoAdicional).all()


def obter_adicional(
    db: Session,
    adicional_id: int,
) -> ProdutoAdicional:
    adicional = (
        db.query(ProdutoAdicional)
        .filter(ProdutoAdicional.id == adicional_id)
        .first()
    )

    if adicional is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adicional nao encontrado",
        )

    return adicional


def criar_adicional(
    db: Session,
    data: ProdutoAdicionalCreate,
) -> ProdutoAdicional:
    produto = db.get(Produto, data.produto_id)

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    adicional = ProdutoAdicional(**data.model_dump())

    try:
        db.add(adicional)
        db.commit()
        db.refresh(adicional)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao criar adicional",
        ) from None

    return adicional


def atualizar_adicional(
    db: Session,
    adicional_id: int,
    data: ProdutoAdicionalUpdate,
) -> ProdutoAdicional:
    adicional = obter_adicional(
        db,
        adicional_id,
    )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(adicional, key, value)

    try:
        db.commit()
        db.refresh(adicional)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao atualizar adicional",
        ) from None

    return adicional


def excluir_adicional(
    db: Session,
    adicional_id: int,
) -> None:
    adicional = obter_adicional(
        db,
        adicional_id,
    )

    try:
        db.delete(adicional)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao excluir adicional",
        ) from None