from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pontos_fidelidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
