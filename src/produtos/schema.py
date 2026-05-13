from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.produtos.model import TipoVariacao


class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)


class CategoriaRead(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SubcategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100)
    categoria_id: int


class SubcategoriaCreate(SubcategoriaBase):
    pass


class SubcategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    categoria_id: Optional[int] = None


class SubcategoriaRead(SubcategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SubcategoriaReadComCategoria(SubcategoriaRead):
    categoria: CategoriaRead


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
