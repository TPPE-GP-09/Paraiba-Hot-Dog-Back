from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)


class CategoriaRead(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
