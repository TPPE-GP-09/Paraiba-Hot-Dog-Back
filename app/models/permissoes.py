from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoPermissao(str, Enum):
    anotar_pedidos = "anotar_pedidos"
    cozinha = "cozinha"
    dashboard = "dashboard"
    configuracoes = "configuracoes"


class Permissao(Base):
    __tablename__ = "permissoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[TipoPermissao] = mapped_column(
        SQLEnum(TipoPermissao, name="tipo_permissao"),
        nullable=False,
        unique=True,
    )
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="permissao")
