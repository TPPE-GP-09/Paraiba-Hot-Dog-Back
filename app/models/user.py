from enum import Enum

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class Role(str, Enum):
    admin = "admin"
    caixa = "caixa"
    cozinha = "cozinha"

role_labels = {
    Role.admin: "Administrador",
    Role.caixa: "Caixa",
    Role.cozinha: "Cozinha",
}

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role, name="user_role"), nullable=False, default=Role.caixa)