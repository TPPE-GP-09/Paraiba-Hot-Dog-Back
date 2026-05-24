from datetime import time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EnderecoBase(BaseModel):
    cep: str
    logradouro: str
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoUpdate(BaseModel):
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None


class EnderecoRead(EnderecoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UnidadeBase(BaseModel):
    nome: str
    imagem: Optional[str] = None
    abertura: time
    fechamento: time
    descricao: Optional[str] = None


class UnidadeCreate(UnidadeBase):
    endereco: EnderecoCreate


class UnidadeUpdate(BaseModel):
    nome: Optional[str] = None
    imagem: Optional[str] = None
    abertura: Optional[time] = None
    fechamento: Optional[time] = None
    descricao: Optional[str] = None
    endereco: Optional[EnderecoUpdate] = None


class UnidadeRead(UnidadeBase):
    id: int
    endereco: EnderecoRead

    model_config = ConfigDict(from_attributes=True)
