from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    pass


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    subcategorias: Mapped[list[Subcategoria]] = relationship(
        "Subcategoria",
        back_populates="categoria",
        cascade="all, delete-orphan",
    )


class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"),
        nullable=False,
    )

    categoria: Mapped[Categoria] = relationship(
        "Categoria",
        back_populates="subcategorias",
        lazy="joined",
    )

    produtos: Mapped[list[Produto]] = relationship(
        "Produto",
        back_populates="subcategoria",
        cascade="all, delete-orphan",
    )


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    imagem_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    subcategoria_id: Mapped[int] = mapped_column(
        ForeignKey("subcategorias.id"),
        nullable=False,
    )

    subcategoria: Mapped[Subcategoria] = relationship(
        "Subcategoria",
        back_populates="produtos",
        lazy="joined",
    )

    variacoes: Mapped[list[ProdutoVariacao]] = relationship(
        "ProdutoVariacao",
        back_populates="produto",
        cascade="all, delete-orphan",
    )

    adicionais: Mapped[list[ProdutoAdicional]] = relationship(
        "ProdutoAdicional",
        back_populates="produto",
        cascade="all, delete-orphan",
    )


class TipoVariacao(str, Enum):
    normal = "normal"
    combo = "combo"


class ProdutoVariacao(Base):
    __tablename__ = "produto_variacoes"

    id: Mapped[int] = mapped_column(primary_key=True)

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id"),
        nullable=False,
    )

    tipo: Mapped[TipoVariacao] = mapped_column(
        SQLEnum(TipoVariacao, name="tipo_variacao"),
        nullable=False,
    )

    preco: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    preco_combo: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    label_combo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    produto: Mapped[Produto] = relationship(
        "Produto",
        back_populates="variacoes",
        lazy="joined",
    )


class ProdutoAdicional(Base):
    __tablename__ = "produto_adicionais"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    preco: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id"),
        nullable=False,
    )

    produto: Mapped[Produto] = relationship(
        "Produto",
        back_populates="adicionais",
        lazy="joined",
    )