from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FormaPagamentoBase(BaseModel):
    nome: str = Field(..., max_length=50)


class FormaPagamentoCreate(FormaPagamentoBase):
    pass


class FormaPagamentoUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=50)


class FormaPagamentoRead(FormaPagamentoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
