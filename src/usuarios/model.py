from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


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
    usuarios: Mapped[list[Usuario]] = relationship(back_populates="permissao")


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

    permissao: Mapped[Permissao | None] = relationship(back_populates="usuarios")
