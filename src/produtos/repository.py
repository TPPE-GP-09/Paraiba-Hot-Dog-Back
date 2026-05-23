from fastapi import HTTPException, status
from sqlalchemy import or_
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
    CategoriaUpdate,
    ProdutoCreate,
    ProdutoUpdate,
    ProdutoVariacaoCreate,
    ProdutoVariacaoUpdate,
    SubcategoriaCreate,
    SubcategoriaUpdate,
    ProdutoAdicionalCreate,
    ProdutoAdicionalUpdate,
)
from src.unidades.model import Unidade


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


def obter_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )
    return categoria


def atualizar_categoria(
    db: Session,
    categoria_id: int,
    data: CategoriaUpdate,
) -> Categoria:
    categoria = obter_categoria(db, categoria_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(categoria, key, value)

    try:
        db.commit()
        db.refresh(categoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao atualizar categoria",
        ) from None

    return categoria


def excluir_categoria(db: Session, categoria_id: int) -> None:
    categoria = obter_categoria(db, categoria_id)
    if categoria.subcategorias:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Categoria possui subcategorias vinculadas",
        )

    try:
        db.delete(categoria)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao excluir categoria",
        ) from None


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


def obter_subcategoria(db: Session, subcategoria_id: int) -> Subcategoria:
    subcategoria = db.get(Subcategoria, subcategoria_id)
    if not subcategoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria nao encontrada",
        )
    return subcategoria


def atualizar_subcategoria(
    db: Session,
    subcategoria_id: int,
    data: SubcategoriaUpdate,
) -> Subcategoria:
    subcategoria = obter_subcategoria(db, subcategoria_id)

    if data.categoria_id is not None and not db.get(Categoria, data.categoria_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nao encontrada",
        )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(subcategoria, key, value)

    try:
        db.commit()
        db.refresh(subcategoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao atualizar subcategoria",
        ) from None

    return subcategoria


def excluir_subcategoria(db: Session, subcategoria_id: int) -> None:
    subcategoria = obter_subcategoria(db, subcategoria_id)
    if subcategoria.produtos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subcategoria possui produtos vinculados",
        )

    try:
        db.delete(subcategoria)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Erro ao excluir subcategoria",
        ) from None


def listar_produtos(
    db: Session,
    skip: int,
    limit: int,
    unidade_id: int | None = None,
) -> list[Produto]:
    query = db.query(Produto)
    if unidade_id is not None:
        query = query.filter(
            or_(
                Produto.disponivel_todas_unidades.is_(True),
                Produto.unidades.any(Unidade.id == unidade_id),
            )
        )
    return query.offset(skip).limit(limit).all()


def obter_produto(db: Session, produto_id: int) -> Produto:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto nao encontrado",
        )

    return produto


def _obter_unidades(db: Session, unidade_ids: list[int]) -> list[Unidade]:
    unidades = db.query(Unidade).filter(Unidade.id.in_(unidade_ids)).all()
    if len(unidades) != len(set(unidade_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade nao encontrada",
        )
    return unidades


def _aplicar_disponibilidade(
    db: Session,
    produto: Produto,
    disponivel_todas_unidades: bool,
    unidade_ids: list[int],
) -> None:
    produto.disponivel_todas_unidades = disponivel_todas_unidades
    if disponivel_todas_unidades:
        produto.unidades = []
        return

    if not unidade_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe ao menos uma unidade para produto restrito",
        )

    produto.unidades = _obter_unidades(db, unidade_ids)


def criar_produto(db: Session, data: ProdutoCreate) -> Produto:
    subcategoria = db.get(Subcategoria, data.subcategoria_id)

    if not subcategoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subcategoria nao encontrada",
        )

    payload = data.model_dump(exclude={"unidade_ids"})
    db_produto = Produto(**payload)
    _aplicar_disponibilidade(
        db,
        db_produto,
        data.disponivel_todas_unidades,
        data.unidade_ids,
    )

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

    payload = data.model_dump(exclude_unset=True, exclude={"unidade_ids"})

    for key, value in payload.items():
        setattr(db_produto, key, value)

    if data.unidade_ids is not None or data.disponivel_todas_unidades is not None:
        _aplicar_disponibilidade(
            db,
            db_produto,
            db_produto.disponivel_todas_unidades,
            data.unidade_ids if data.unidade_ids is not None else db_produto.unidade_ids,
        )

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
