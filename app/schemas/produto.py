from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    preco: float = Field(..., gt=0)
    preco_combo: Optional[float] = Field(None, gt=0)
    categoria: str = Field(..., max_length=100)
    esta_ativo: bool = True
    observacao: Optional[str] = None
    imagem: Optional[str] = None
    unidade_id: Optional[int] = None


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None, max_length=500)
    preco: Optional[float] = Field(None, gt=0)
    preco_combo: Optional[float] = Field(None, gt=0)
    categoria: Optional[str] = Field(None, max_length=100)
    esta_ativo: Optional[bool] = None
    observacao: Optional[str] = None
    imagem: Optional[str] = None
    unidade_id: Optional[int] = None


class ProdutoRead(ProdutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
