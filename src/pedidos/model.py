from sqlalchemy import Column, Float, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.produtos.model import Produto
from src.usuarios.model import Usuario

pedido_produtos = Table(
    "pedido_produtos",
    Base.metadata,
    Column("pedido_id", ForeignKey("pedidos.id"), primary_key=True),
    Column("produto_id", ForeignKey("produtos.id"), primary_key=True),
)

class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    metodo_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    preco_total: Mapped[float] = mapped_column(Float, nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Recebido", server_default="Recebido", nullable=False)

    usuario: Mapped[Usuario] = relationship("Usuario")
    produtos: Mapped[list[Produto]] = relationship("Produto", secondary=pedido_produtos)
