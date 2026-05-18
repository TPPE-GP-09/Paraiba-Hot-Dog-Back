from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.clientes import repository
from src.clientes.repository import _mapear_erro_integridade
from src.clientes.schema import ClienteCreate, ClienteRead, ClienteUpdate
from src.database import get_db

router = APIRouter()


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def criar_cliente(data: ClienteCreate, db: Session = Depends(get_db)) -> ClienteRead:
    try:
        cliente = repository.criar_cliente(db, data)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409, detail=_mapear_erro_integridade(e)) from e
    return ClienteRead.model_validate(cliente)


@router.get("/", response_model=list[ClienteRead])
def listar_clientes(
    telefone: str | None = Query(default=None),
    nome: str | None = Query(default=None),
    email: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, gt=0),
    db: Session = Depends(get_db),
) -> list[ClienteRead]:
    clientes = repository.listar_clientes(
        db, telefone, nome, email, skip, limit)
    return [ClienteRead.model_validate(c) for c in clientes]


@router.get("/{cliente_id}", response_model=ClienteRead)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)) -> ClienteRead:
    cliente = repository.obter_cliente(db, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return ClienteRead.model_validate(cliente)


@router.patch("/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente(cliente_id: int, data: ClienteUpdate, db: Session = Depends(get_db)) -> ClienteRead:
    try:
        cliente = repository.atualizar_cliente(db, cliente_id, data)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=409, detail=_mapear_erro_integridade(e)) from e
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return ClienteRead.model_validate(cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = repository.excluir_cliente(db, cliente_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cliente nao encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
