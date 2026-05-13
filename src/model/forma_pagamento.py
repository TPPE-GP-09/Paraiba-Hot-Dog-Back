from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class FormaPagamento(Base):
    __tablename__ = "formas_pagamento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
