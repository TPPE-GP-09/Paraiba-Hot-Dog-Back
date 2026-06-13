from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.bi import repository
from src.bi.schema import BiDashboardRead
from src.database import get_db

router = APIRouter()

@router.get("/dashboard", response_model=BiDashboardRead)
def obter_dashboard(
    unidade_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
) -> BiDashboardRead:
    """Retorna os indicadores agregados da tela de BI."""
    return repository.obter_dashboard(db, unidade_id)
