from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.forma_pagamento import FormaPagamentoRead


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
