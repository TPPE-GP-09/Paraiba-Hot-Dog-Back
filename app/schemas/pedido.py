from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.produto import ProdutoRead

class PedidoBase(BaseModel):
    metodo_pagamento: str = Field(..., max_length=50)
    preco_total: float = Field(..., ge=0)
    usuario_id: int
    unidade_id: int

class PedidoCreate(PedidoBase):
    produtos_ids: list[int]

class PedidoUpdate(BaseModel):
    metodo_pagamento: Optional[str] = Field(None, max_length=50)
    preco_total: Optional[float] = Field(None, ge=0)
    usuario_id: Optional[int] = None
    unidade_id: Optional[int] = None
    produtos_ids: Optional[list[int]] = None

class PedidoRead(PedidoBase):
    id: int
    produtos: list[ProdutoRead] = []

    model_config = ConfigDict(from_attributes=True)
