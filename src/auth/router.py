from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.database import get_db
from src.jwt_auth import create_access_token, verify_password, hash_password
from src.usuarios.model import Usuario

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user with email and password, return JWT token."""
    user = db.query(Usuario).filter(Usuario.email == str(credentials.email)).first()

    if not user or not user.senha_hash or not verify_password(
        credentials.password, user.senha_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "nome": user.nome,
            "roles": [user.funcao.value] if user.funcao else [],
        }
    )

    return TokenResponse(access_token=access_token)
