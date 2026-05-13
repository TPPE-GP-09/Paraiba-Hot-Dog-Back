from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.forma_pagamento import FormaPagamento
    from app.models.pedido import Pedido


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
