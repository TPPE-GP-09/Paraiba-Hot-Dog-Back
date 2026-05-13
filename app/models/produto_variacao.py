from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.produto import Produto


class TipoVariacao(str, Enum):
    normal = "normal"
    combo = "combo"


class ProdutoVariacao(Base):
    __tablename__ = "produto_variacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    tipo: Mapped[TipoVariacao] = mapped_column(
        SQLEnum(TipoVariacao, name="tipo_variacao"),
        nullable=False,
    )
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_combo: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    label_combo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    produto: Mapped[Produto] = relationship("Produto", back_populates="variacoes", lazy="joined")
