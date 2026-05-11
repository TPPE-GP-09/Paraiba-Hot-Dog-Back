from enum import Enum

from pydantic import BaseModel, ConfigDict


class TipoPermissao(str, Enum):
    anotar_pedidos = "anotar_pedidos"
    cozinha = "cozinha"
    dashboard = "dashboard"
    configuracoes = "configuracoes"


class PermissaoBase(BaseModel):
    nome: TipoPermissao


class PermissaoCreate(PermissaoBase):
    pass


class PermissaoRead(PermissaoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
