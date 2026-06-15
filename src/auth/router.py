from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.auth import repository
from src.database import get_db

router = APIRouter()


class EsqueciSenhaRequest(BaseModel):
    email: EmailStr


class EsqueciSenhaResponse(BaseModel):
    message: str
    email_status: str


class RedefinirSenhaRequest(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8)


@router.post(
    "/esqueci-senha",
    response_model=EsqueciSenhaResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def esqueci_senha(
    payload: EsqueciSenhaRequest,
    db: Session = Depends(get_db),
) -> EsqueciSenhaResponse:
    resultado = repository.solicitar_recuperacao_senha(db, str(payload.email))

    return EsqueciSenhaResponse(
        message=resultado["message"],
        email_status=resultado["email_status"],
    )


@router.post("/redefinir-senha", status_code=status.HTTP_204_NO_CONTENT)
def redefinir_senha(
    payload: RedefinirSenhaRequest,
    db: Session = Depends(get_db),
) -> None:
    repository.redefinir_senha(db, payload.token, payload.nova_senha)
