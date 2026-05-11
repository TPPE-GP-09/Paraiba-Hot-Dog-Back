from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.produto import Produto
from app.schemas.produto import ProdutoCreate, ProdutoRead, ProdutoUpdate

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("/", response_model=List[ProdutoRead], summary="Listar todos os produtos")
def listar_produtos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os produtos cadastrados no sistema."""
    produtos = db.query(Produto).offset(skip).limit(limit).all()
    return produtos


@router.get("/{produto_id}", response_model=ProdutoRead, summary="Obter um produto pelo ID")
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Obtém os detalhes de um produto específico através do seu ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")
    return produto


@router.post("/", response_model=ProdutoRead, status_code=status.HTTP_201_CREATED, summary="Criar um novo produto")
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    """Cria um novo produto e o salva no banco de dados."""
    db_produto = Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.put("/{produto_id}", response_model=ProdutoRead, summary="Atualizar um produto")
def atualizar_produto(produto_id: int, produto_update: ProdutoUpdate, db: Session = Depends(get_db)):
    """Atualiza as informações de um produto existente através do seu ID."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if db_produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")
    
    update_data = produto_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_produto, key, value)
        
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir um produto")
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    """Exclui um produto do banco de dados através do seu ID."""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if db_produto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto nao encontrado")
    
    db.delete(db_produto)
    db.commit()
    return None
