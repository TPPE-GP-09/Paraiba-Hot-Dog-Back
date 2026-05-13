from datetime import datetime, time, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
)
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


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    subcategorias: Mapped[list["Subcategoria"]] = relationship("Subcategoria", back_populates="categoria")


class Subcategoria(Base):
    __tablename__ = "subcategorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)

    categoria: Mapped[Categoria] = relationship("Categoria", back_populates="subcategorias", lazy="joined")
    produtos: Mapped[list["Produto"]] = relationship("Produto", back_populates="subcategoria")


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    imagem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    subcategoria_id: Mapped[int] = mapped_column(ForeignKey("subcategorias.id"), nullable=False)

    subcategoria: Mapped[Subcategoria] = relationship("Subcategoria", back_populates="produtos", lazy="joined")
    variacoes: Mapped[list["ProdutoVariacao"]] = relationship("ProdutoVariacao", back_populates="produto")


class TipoVariacao(str, Enum):
    normal = "normal"
    combo = "combo"


class ProdutoVariacao(Base):
    __tablename__ = "produto_variacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    tipo: Mapped[TipoVariacao] = mapped_column(
        SQLEnum(TipoVariacao, name="tipo_variacao"),
        nullable=False,
    )
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    preco_combo: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    label_combo: Mapped[str | None] = mapped_column(String(50), nullable=True)

    produto: Mapped[Produto] = relationship("Produto", back_populates="variacoes", lazy="joined")


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pontos_fidelidade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class FormaPagamento(Base):
    __tablename__ = "formas_pagamento"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


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


class StatusPedido(str, Enum):
    preparando = "preparando"
    entregue = "entregue"
    cancelado = "cancelado"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), nullable=False)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("clientes.id"), nullable=True)
    status: Mapped[StatusPedido] = mapped_column(
        SQLEnum(StatusPedido, name="status_pedido"),
        nullable=False,
        default=StatusPedido.preparando,
    )

    mesa: Mapped[Mesa] = relationship("Mesa", lazy="joined")
    cliente: Mapped["Cliente | None"] = relationship("Cliente", lazy="joined")
    itens: Mapped[list["ItemPedido"]] = relationship("ItemPedido", back_populates="pedido")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    variacao_id: Mapped[int] = mapped_column(ForeignKey("produto_variacoes.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship("Pedido", back_populates="itens")
    variacao: Mapped[ProdutoVariacao] = relationship("ProdutoVariacao", lazy="joined")
    adicionais: Mapped[list["Adicional"]] = relationship("Adicional", back_populates="item_pedido")


class Adicional(Base):
    __tablename__ = "adicionais"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_pedido_id: Mapped[int] = mapped_column(ForeignKey("itens_pedido.id"), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)

    item_pedido: Mapped[ItemPedido] = relationship("ItemPedido", back_populates="adicionais")


class PedidoPagamento(Base):
    __tablename__ = "pedido_pagamento"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    forma_pagamento_id: Mapped[int] = mapped_column(ForeignKey("formas_pagamento.id"), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    taxas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default="0")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    pedido: Mapped[Pedido] = relationship("Pedido", lazy="joined")
    forma_pagamento: Mapped[FormaPagamento] = relationship("FormaPagamento", lazy="joined")
