from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AdicionalBase(BaseModel):
    item_pedido_id: int
    descricao: str = Field(..., max_length=255)


class AdicionalCreate(AdicionalBase):
    pass


class AdicionalUpdate(BaseModel):
    descricao: Optional[str] = Field(None, max_length=255)


class AdicionalRead(AdicionalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
