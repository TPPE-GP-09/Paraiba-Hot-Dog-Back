from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.produtos import repository
from src.produtos.schema import ProdutoCreate, ProdutoRead, ProdutoUpdate

router = APIRouter()


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
