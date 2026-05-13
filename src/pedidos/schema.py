from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.clientes.schema import ClienteRead
from src.mesas.schema import MesaRead
from src.pagamentos.schema import FormaPagamentoRead
from src.pedidos.model import StatusPedido
from src.produtos.schema import ProdutoVariacaoRead


class AdicionalBase(BaseModel):
    item_pedido_id: int
    descricao: str = Field(..., max_length=255)


class AdicionalCreate(AdicionalBase):
    pass


class AdicionalUpdate(BaseModel):
    descricao: Optional[str] = Field(None, max_length=255)


class AdicionalRead(AdicionalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoBase(BaseModel):
    pedido_id: int
    variacao_id: int
    quantidade: int = Field(1, ge=1)
    observacao: Optional[str] = None
    preco_unitario: Decimal = Field(..., gt=0, decimal_places=2)


class ItemPedidoCreate(ItemPedidoBase):
    pass


class ItemPedidoUpdate(BaseModel):
    quantidade: Optional[int] = Field(None, ge=1)
    observacao: Optional[str] = None


class ItemPedidoRead(ItemPedidoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoReadCompleto(ItemPedidoRead):
    variacao: ProdutoVariacaoRead
    adicionais: list[AdicionalRead] = []


class PedidoBase(BaseModel):
    mesa_id: int
    cliente_id: Optional[int] = None
    status: StatusPedido = StatusPedido.preparando


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    status: Optional[StatusPedido] = None
    cliente_id: Optional[int] = None


class PedidoRead(PedidoBase):
    id: int
    hora: datetime

    model_config = ConfigDict(from_attributes=True)


class PedidoReadCompleto(PedidoRead):
    mesa: MesaRead
    cliente: Optional[ClienteRead] = None
    itens: list[ItemPedidoReadCompleto] = []


class PedidoPagamentoBase(BaseModel):
    pedido_id: int
    forma_pagamento_id: int
    subtotal: Decimal = Field(..., ge=0, decimal_places=2)
    taxas: Decimal = Field(Decimal("0"), ge=0, decimal_places=2)
    total: Decimal = Field(..., ge=0, decimal_places=2)


class PedidoPagamentoCreate(PedidoPagamentoBase):
    pass


class PedidoPagamentoUpdate(BaseModel):
    forma_pagamento_id: Optional[int] = None
    subtotal: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    taxas: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    total: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class PedidoPagamentoRead(PedidoPagamentoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PedidoPagamentoReadCompleto(PedidoPagamentoRead):
    forma_pagamento: FormaPagamentoRead
