from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.categoria import CategoriaRead


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
