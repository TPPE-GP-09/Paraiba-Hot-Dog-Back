from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.pedido import StatusPedido
from app.schemas.cliente import ClienteRead
from app.schemas.item_pedido import ItemPedidoReadCompleto
from app.schemas.mesa import MesaRead


class PedidoBase(BaseModel):
    mesa_id: int
    cliente_id: Optional[int] = None
    status: StatusPedido = StatusPedido.preparando


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    status: Optional[StatusPedido] = None
    cliente_id: Optional[int] = None


class PedidoRead(PedidoBase):
    id: int
    hora: datetime

    model_config = ConfigDict(from_attributes=True)


class PedidoReadCompleto(PedidoRead):
    mesa: MesaRead
    cliente: Optional[ClienteRead] = None
    itens: list[ItemPedidoReadCompleto] = []
