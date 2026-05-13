from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.model.cliente import Cliente
    from src.model.item_pedido import ItemPedido
    from src.model.mesa import Mesa


class StatusPedido(str, Enum):
    preparando = "preparando"
    entregue = "entregue"
    cancelado = "cancelado"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
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
