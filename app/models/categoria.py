from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    subcategorias: Mapped[list[Subcategoria]] = relationship("Subcategoria", back_populates="categoria")


from app.models.subcategoria import Subcategoria  # noqa: E402, F401
