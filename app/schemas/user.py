from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class Role(str, Enum):
    admin = "admin"
    caixa = "caixa"
    cozinha = "cozinha"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Role = Role.caixa

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)