from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.produtos.schema import ProdutoRead

class PedidoBase(BaseModel):
    metodo_pagamento: str = Field(..., max_length=50)
    usuario_id: int
    unidade_id: int

class PedidoCreate(PedidoBase):
    produtos_ids: List[int]

    @field_validator('metodo_pagamento')
    @classmethod
    def validar_metodo_pagamento(cls, v: str) -> str:
        metodos_validos = ['PIX', 'Crédito', 'Dinheiro', 'Débito']
        if v not in metodos_validos:
            raise ValueError(f'Método de pagamento inválido. Escolha entre: {", ".join(metodos_validos)}')
        return v

class PedidoUpdate(BaseModel):
    metodo_pagamento: Optional[str] = Field(None, max_length=50)
    preco_total: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=50)
    usuario_id: Optional[int] = None
    unidade_id: Optional[int] = None
    produtos_ids: Optional[List[int]] = None

class PedidoRead(PedidoBase):
    id: int
    preco_total: float
    status: str
    produtos: List[ProdutoRead] = []

    model_config = ConfigDict(from_attributes=True)
