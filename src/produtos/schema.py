from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(..., max_length=255)
    descricao: Optional[str] = None
    imagem_url: Optional[str] = Field(None, max_length=500)
    ativo: bool = True
    subcategoria_id: int


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = None
    imagem_url: Optional[str] = Field(None, max_length=500)
    ativo: Optional[bool] = None
    subcategoria_id: Optional[int] = None


class ProdutoRead(ProdutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
