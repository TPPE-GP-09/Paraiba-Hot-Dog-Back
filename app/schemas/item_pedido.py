from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.adicional import AdicionalRead
from app.schemas.produto_variacao import ProdutoVariacaoRead


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
