from sqlalchemy import String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    esta_ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
