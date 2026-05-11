from datetime import time

from pydantic import BaseModel, ConfigDict

from src.enderecos.schema import EnderecoCreate, EnderecoRead


class UnidadeBase(BaseModel):
    nome: str
    imagem: str | None = None
    abertura: time
    fechamento: time
    descricao: str | None = None


class UnidadeCreate(UnidadeBase):
    endereco: EnderecoCreate


class UnidadeRead(UnidadeBase):
    id: int
    endereco: EnderecoRead
    model_config = ConfigDict(from_attributes=True)
