from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.clientes.model import Cliente
from src.clientes.schema import ClienteCreate, ClienteUpdate


def _mapear_erro_integridade(error: IntegrityError) -> str:
    message = str(error.orig)
    if "telefone" in message:
        return "Telefone ja cadastrado"
    if "email" in message:
        return "Email ja cadastrado"
    return "Violacao de integridade"


def listar_clientes(
    db: Session,
    telefone: str | None,
    nome: str | None,
    email: str | None,
    skip: int = 0,
    limit: int = 100,
) -> list[Cliente]:
    query = db.query(Cliente).filter(Cliente.ativo.is_(True))
    if telefone:
        query = query.filter(Cliente.telefone == telefone)
    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Cliente.email == email)
    return query.order_by(Cliente.id.asc()).offset(skip).limit(limit).all()


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
