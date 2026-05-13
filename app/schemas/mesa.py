from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.mesa import StatusMesa


class MesaBase(BaseModel):
    numero: int
    status: StatusMesa = StatusMesa.livre


class MesaCreate(MesaBase):
    pass


class MesaUpdate(BaseModel):
    numero: Optional[int] = None
    status: Optional[StatusMesa] = None


class MesaRead(MesaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
