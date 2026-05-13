from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.model.categoria import Categoria
    from src.model.produto import Produto


class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)

    categoria: Mapped[Categoria] = relationship("Categoria", back_populates="subcategorias", lazy="joined")
    produtos: Mapped[list[Produto]] = relationship("Produto", back_populates="subcategoria")
