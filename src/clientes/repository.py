from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.clientes.model import Cliente
from src.clientes.schema import ClienteCreate, ClienteFiltro, ClienteUpdate


def _mapear_erro_integridade(error: IntegrityError) -> str:
    message = str(error.orig)
    if "telefone" in message:
        return "Telefone ja cadastrado"
    if "email" in message:
        return "Email ja cadastrado"
    return "Violacao de integridade"


def listar_clientes(db: Session, filtro: ClienteFiltro) -> list[Cliente]:
    query = db.query(Cliente).filter(Cliente.ativo.is_(True))
    if filtro.telefone:
        query = query.filter(Cliente.telefone == filtro.telefone)
    if filtro.nome:
        query = query.filter(Cliente.nome.ilike(f"%{filtro.nome}%"))
    if filtro.email:
        query = query.filter(Cliente.email == filtro.email)
    return query.order_by(Cliente.id.asc()).offset(filtro.skip).limit(filtro.limit).all()


def obter_cliente(db: Session, cliente_id: int) -> Cliente | None:
    return (
        db.query(Cliente)
        .filter(Cliente.id == cliente_id, Cliente.ativo.is_(True))
        .first()
    )


def criar_cliente(db: Session, data: ClienteCreate) -> Cliente:
    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def atualizar_cliente(db: Session, cliente_id: int, data: ClienteUpdate) -> Cliente | None:
    cliente = obter_cliente(db, cliente_id)
    if not cliente:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente


def excluir_cliente(db: Session, cliente_id: int) -> bool:
    cliente = obter_cliente(db, cliente_id)
    if not cliente:
        return False
    cliente.ativo = False
    db.commit()
    return True
