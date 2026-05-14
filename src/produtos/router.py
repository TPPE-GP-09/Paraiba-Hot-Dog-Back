from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.produtos import repository
from src.produtos.schema import (
    CategoriaCreate,
    CategoriaRead,
    ProdutoCreate,
    ProdutoRead,
    ProdutoUpdate,
    SubcategoriaCreate,
    SubcategoriaRead,
)

router = APIRouter()


@router.get("/categorias", response_model=list[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db)):
    return repository.listar_categorias(db)


@router.post("/categorias", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def criar_categoria(data: CategoriaCreate, db: Session = Depends(get_db)):
    return repository.criar_categoria(db, data)


@router.get("/subcategorias", response_model=list[SubcategoriaRead])
def listar_subcategorias(db: Session = Depends(get_db)):
    return repository.listar_subcategorias(db)


@router.post("/subcategorias", response_model=SubcategoriaRead, status_code=status.HTTP_201_CREATED)
def criar_subcategoria(data: SubcategoriaCreate, db: Session = Depends(get_db)):
    return repository.criar_subcategoria(db, data)


@router.get("/", response_model=list[ProdutoRead])
def listar_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repository.listar_produtos(db, skip, limit)


@router.get("/{produto_id}", response_model=ProdutoRead)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    return repository.obter_produto(db, produto_id)


@router.post("/", response_model=ProdutoRead, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    return repository.criar_produto(db, produto)


@router.put("/{produto_id}", response_model=ProdutoRead)
def atualizar_produto(produto_id: int, data: ProdutoUpdate, db: Session = Depends(get_db)):
    return repository.atualizar_produto(db, produto_id, data)


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    repository.excluir_produto(db, produto_id)
