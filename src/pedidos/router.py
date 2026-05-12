from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.pedidos.model import Pedido
from src.produtos.model import Produto
from src.pedidos.schema import PedidoCreate, PedidoRead

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@router.post("/", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, summary="Criar um novo pedido", description="Cria um novo pedido calculando automaticamente o preço total com base nos produtos selecionados. Métodos de pagamento aceitos: PIX, Crédito, Dinheiro, Débito.")
def criar_pedido(pedido_in: PedidoCreate, db: Session = Depends(get_db)):
    """Cria um pedido, calculando o valor total e vinculando os produtos."""
    produtos_ids_unicos = list(set(pedido_in.produtos_ids))
    produtos = db.query(Produto).filter(Produto.id.in_(produtos_ids_unicos)).all()

    if len(produtos) != len(produtos_ids_unicos):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Um ou mais produtos não encontrados.")

    preco_total = sum(p.preco for p in produtos)

    db_pedido = Pedido(
        metodo_pagamento=pedido_in.metodo_pagamento,
        preco_total=preco_total,
        status="Recebido",
        usuario_id=pedido_in.usuario_id,
        unidade_id=pedido_in.unidade_id
    )

    db_pedido.produtos = produtos

    db.add(db_pedido)
    db.commit()
    db.refresh(db_pedido)
    return db_pedido

@router.get("/", response_model=List[PedidoRead], summary="Listar todos os pedidos", description="Retorna a lista de todos os pedidos com os detalhes dos produtos associados.")
def listar_pedidos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os pedidos cadastrados."""
    pedidos = db.query(Pedido).offset(skip).limit(limit).all()
    return pedidos

@router.get("/{pedido_id}", response_model=PedidoRead, summary="Obter um pedido pelo ID", description="Busca os detalhes de um pedido específico utilizando o seu identificador.")
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Busca um pedido específico por ID."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado.")
    return pedido

@router.get("/usuario/{usuario_id}", response_model=List[PedidoRead], summary="Histórico de pedidos de um usuário", description="Lista o histórico de todos os pedidos realizados por um determinado usuário (cliente).")
def listar_pedidos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Lista o histórico de pedidos de um usuário."""
    pedidos = db.query(Pedido).filter(Pedido.usuario_id == usuario_id).all()
    return pedidos
