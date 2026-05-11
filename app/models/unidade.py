from datetime import time

from sqlalchemy import ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.endereco import Endereco


class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    imagem: Mapped[str | None] = mapped_column(String(500), nullable=True)
    abertura: Mapped[time] = mapped_column(Time, nullable=False)
    fechamento: Mapped[time] = mapped_column(Time, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    endereco_id: Mapped[int] = mapped_column(ForeignKey("enderecos.id"), nullable=False)

    endereco: Mapped[Endereco] = relationship("Endereco", lazy="joined")
