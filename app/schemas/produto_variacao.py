from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.produto_variacao import TipoVariacao


class ProdutoVariacaoBase(BaseModel):
    produto_id: int
    tipo: TipoVariacao
    preco: Decimal = Field(..., gt=0, decimal_places=2)
    preco_combo: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    label_combo: Optional[str] = Field(None, max_length=50)


class ProdutoVariacaoCreate(ProdutoVariacaoBase):
    pass


class ProdutoVariacaoUpdate(BaseModel):
    tipo: Optional[TipoVariacao] = None
    preco: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    preco_combo: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    label_combo: Optional[str] = Field(None, max_length=50)


class ProdutoVariacaoRead(ProdutoVariacaoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
