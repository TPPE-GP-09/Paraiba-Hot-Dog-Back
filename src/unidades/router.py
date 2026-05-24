from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.unidades import repository
from src.unidades.schema import UnidadeCreate, UnidadeRead, UnidadeUpdate
from src.security import get_current_user

router = APIRouter()


@router.get("/", response_model=list[UnidadeRead])
def listar_unidades(db: Session = Depends(get_db)):
    return repository.listar_unidades(db)


@router.get("/{unidade_id}", response_model=UnidadeRead)
def obter_unidade(unidade_id: int, db: Session = Depends(get_db)):
    return repository.obter_unidade(db, unidade_id)


@router.post(
    "/",
    response_model=UnidadeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def criar_unidade(data: UnidadeCreate, db: Session = Depends(get_db)):
    return repository.criar_unidade(db, data)


@router.patch(
    "/{unidade_id}",
    response_model=UnidadeRead,
    dependencies=[Depends(get_current_user)],
)
def atualizar_unidade(unidade_id: int, data: UnidadeUpdate, db: Session = Depends(get_db)):
    return repository.atualizar_unidade(db, unidade_id, data)


@router.delete(
    "/{unidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_user)],
)
def excluir_unidade(unidade_id: int, db: Session = Depends(get_db)):
    repository.excluir_unidade(db, unidade_id)
