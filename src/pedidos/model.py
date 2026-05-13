from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.clientes.model import Cliente
    from src.mesas.model import Mesa
    from src.pagamentos.model import FormaPagamento
    from src.produtos.model import ProdutoVariacao


class StatusPedido(str, Enum):
    preparando = "preparando"
    entregue = "entregue"
    cancelado = "cancelado"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), nullable=False)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    status: Mapped[StatusPedido] = mapped_column(
        SQLEnum(StatusPedido, name="status_pedido"),
        nullable=False,
        default=StatusPedido.preparando,
    )

    mesa: Mapped[Mesa] = relationship("Mesa", lazy="joined")
    cliente: Mapped[Cliente | None] = relationship("Cliente", lazy="joined")
    itens: Mapped[list[ItemPedido]] = relationship("ItemPedido", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    variacao_id: Mapped[int] = mapped_column(ForeignKey("produto_variacoes.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship("Pedido", back_populates="itens")
    variacao: Mapped[ProdutoVariacao] = relationship("ProdutoVariacao", lazy="joined")
    adicionais: Mapped[list[Adicional]] = relationship("Adicional", back_populates="item_pedido")


class Adicional(Base):
    __tablename__ = "adicionais"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_pedido_id: Mapped[int] = mapped_column(ForeignKey("itens_pedido.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    item_pedido: Mapped[ItemPedido] = relationship("ItemPedido", back_populates="adicionais")


class PedidoPagamento(Base):
    __tablename__ = "pedido_pagamento"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    forma_pagamento_id: Mapped[int] = mapped_column(ForeignKey("formas_pagamento.id"), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    taxas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default="0")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship("Pedido", lazy="joined")
    forma_pagamento: Mapped[FormaPagamento] = relationship("FormaPagamento", lazy="joined")
