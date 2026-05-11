from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.unidade import Unidade


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    preco_combo: Mapped[float | None] = mapped_column(Float, nullable=True)
    categoria: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    esta_ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagem: Mapped[str | None] = mapped_column(String(500), nullable=True)
    unidade_id: Mapped[int | None] = mapped_column(ForeignKey("unidades.id"), nullable=True)

    unidade: Mapped[Unidade | None] = relationship("Unidade", lazy="joined")
