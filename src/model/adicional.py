from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.model.item_pedido import ItemPedido


class Adicional(Base):
    __tablename__ = "adicionais"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_pedido_id: Mapped[int] = mapped_column(ForeignKey("itens_pedido.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    item_pedido: Mapped[ItemPedido] = relationship("ItemPedido", back_populates="adicionais")
