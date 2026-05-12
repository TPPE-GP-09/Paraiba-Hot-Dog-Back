from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr

from src.permissoes.schema import PermissaoRead


class FuncaoUsuario(str, Enum):
    administrador = "administrador"
    caixa = "caixa"
    cozinha = "cozinha"


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    funcao: FuncaoUsuario = FuncaoUsuario.caixa
    unidade_id: int | None = None
    permissao_id: int | None = None


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    senha: str | None = None
    funcao: FuncaoUsuario | None = None
    unidade_id: int | None = None
    permissao_id: int | None = None


class UsuarioRead(UsuarioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UsuarioReadComPermissao(UsuarioRead):
    permissao: PermissaoRead | None = None
