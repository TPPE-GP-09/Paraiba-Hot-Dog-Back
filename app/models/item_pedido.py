from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.adicional import Adicional
    from app.models.pedido import Pedido
    from app.models.produto_variacao import ProdutoVariacao


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
