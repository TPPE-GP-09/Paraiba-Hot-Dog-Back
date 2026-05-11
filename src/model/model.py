from datetime import time
from enum import Enum

from sqlalchemy import Boolean, Enum as SQLEnum, Float, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
