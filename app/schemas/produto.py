from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    preco: float = Field(..., gt=0)
    categoria: str = Field(..., max_length=100)
    esta_ativo: bool = True


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    preco: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    esta_ativo: Optional[bool] = None


class ProdutoRead(ProdutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
