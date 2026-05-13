from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=120)
    telefone: Optional[str] = Field(None, max_length=20)
    pontos_fidelidade: int = 0


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=120)
    telefone: Optional[str] = Field(None, max_length=20)
    pontos_fidelidade: Optional[int] = None


class ClienteRead(ClienteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
