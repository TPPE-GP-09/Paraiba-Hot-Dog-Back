from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr

class Role(str, Enum):
    admin = "0"
    caixa = "1"
    cozinha = "2"

class UserBase(BaseModel):
    email: EmailStr
    role: Role = Role.caixa

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)