from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.permissoes.model import TipoPermissao


class PermissaoBase(BaseModel):
    nome: TipoPermissao


class PermissaoCreate(PermissaoBase):
    pass


class PermissaoRead(PermissaoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class FuncaoUsuario(str, Enum):
    administrador = "administrador"
    caixa = "caixa"
    cozinha = "cozinha"


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    funcao: FuncaoUsuario = FuncaoUsuario.caixa
    unidade_id: int | None = Field(None, gt=0)


class UsuarioCreate(UsuarioBase):
    senha: str
    permissao_ids: list[int] = Field(default_factory=list)


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    senha: str | None = None
    funcao: FuncaoUsuario | None = None
    unidade_id: int | None = Field(None, gt=0)
    permissao_ids: list[int] | None = None


class UsuarioRead(UsuarioBase):
    id: int
    permissoes: list[PermissaoRead] = []
    model_config = ConfigDict(from_attributes=True)
