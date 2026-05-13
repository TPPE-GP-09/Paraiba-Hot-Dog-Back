from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.model.produto_variacao import ProdutoVariacao
    from src.model.subcategoria import Subcategoria


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subcategoria_id: Mapped[int] = mapped_column(ForeignKey("subcategorias.id"), nullable=False)

    subcategoria: Mapped[Subcategoria] = relationship("Subcategoria", back_populates="produtos", lazy="joined")
    variacoes: Mapped[list[ProdutoVariacao]] = relationship("ProdutoVariacao", back_populates="produto")
