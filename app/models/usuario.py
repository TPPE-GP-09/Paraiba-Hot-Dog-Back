from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.permissoes import Permissao


class FuncaoUsuario(str, Enum):
    administrador = "administrador"
    caixa = "caixa"
    cozinha = "cozinha"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    funcao: Mapped[FuncaoUsuario] = mapped_column(
        SQLEnum(FuncaoUsuario, name="funcao_usuario"),
        nullable=False,
        default=FuncaoUsuario.caixa,
    )
    unidade_id: Mapped[int | None] = mapped_column(nullable=True)
    permissao_id: Mapped[int | None] = mapped_column(ForeignKey("permissoes.id"), nullable=True)

    permissao: Mapped["Permissao | None"] = relationship(back_populates="usuarios")
