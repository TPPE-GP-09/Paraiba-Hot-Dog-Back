from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.config import settings

router = APIRouter()


class SeedRequest(BaseModel):
    secret: str


@router.post("/seed", status_code=status.HTTP_200_OK)
def executar_seed(payload: SeedRequest) -> dict:
    if not settings.seed_secret_key or payload.secret != settings.seed_secret_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chave invalida")

    try:
        from scripts.seed import run
        run()
        return {"status": "ok", "message": "Seeds aplicados com sucesso"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao aplicar seeds: {exc}",
        ) from exc
