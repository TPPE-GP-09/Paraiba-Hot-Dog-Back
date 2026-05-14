from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.produtos.model import Categoria, Produto, Subcategoria
from src.produtos.schema import (
    CategoriaCreate,
    ProdutoCreate,
    ProdutoUpdate,
    SubcategoriaCreate,
)


def listar_categorias(db: Session) -> list[Categoria]:
    return db.query(Categoria).all()


def criar_categoria(db: Session, data: CategoriaCreate) -> Categoria:
    obj = Categoria(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def listar_subcategorias(db: Session) -> list[Subcategoria]:
    return db.query(Subcategoria).all()


def criar_subcategoria(db: Session, data: SubcategoriaCreate) -> Subcategoria:
    if not db.get(Categoria, data.categoria_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria nao encontrada")
    obj = Subcategoria(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def listar_produtos(db: Session, skip: int, limit: int) -> list[Produto]:
    return db.query(Produto).offset(skip).limit(limit).all()


def obter_produto(db: Session, produto_id: int) -> Produto:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")
    return produto


def criar_produto(db: Session, data: ProdutoCreate) -> Produto:
    db_produto = Produto(**data.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


def atualizar_produto(db: Session, produto_id: int, data: ProdutoUpdate) -> Produto:
    db_produto = obter_produto(db, produto_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_produto, key, value)
    db.commit()
    db.refresh(db_produto)
    return db_produto


def excluir_produto(db: Session, produto_id: int) -> None:
    db_produto = obter_produto(db, produto_id)
    db.delete(db_produto)
    db.commit()
