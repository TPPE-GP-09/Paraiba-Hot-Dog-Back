from enum import Enum

from sqlalchemy import Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class StatusMesa(str, Enum):
    livre = "livre"
    ocupada = "ocupada"


class Mesa(Base):
    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[StatusMesa] = mapped_column(
        SQLEnum(StatusMesa, name="status_mesa"),
        nullable=False,
        default=StatusMesa.livre,
    )
