from pydantic import BaseModel, ConfigDict


class EnderecoBase(BaseModel):
    cep: str
    logradouro: str
    numero: str | None = None
    complemento: str | None = None
    bairro: str
    cidade: str
    estado: str


class EnderecoCreate(EnderecoBase):
    pass


class EnderecoRead(EnderecoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
