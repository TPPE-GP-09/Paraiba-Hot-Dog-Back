from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Endereco(Base):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cep: Mapped[str] = mapped_column(String(8), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[str | None] = mapped_column(String(10), nullable=True)
    complemento: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bairro: Mapped[str] = mapped_column(String(255), nullable=False)
    cidade: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
