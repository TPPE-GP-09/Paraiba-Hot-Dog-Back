from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.permissoes import repository
from src.usuarios.schema import PermissaoRead

router = APIRouter()


@router.get("/", response_model=list[PermissaoRead])
def listar_permissoes(db: Session = Depends(get_db)):
    return repository.listar_permissoes(db)


@router.get("/{permissao_id}", response_model=PermissaoRead)
def obter_permissao(permissao_id: int, db: Session = Depends(get_db)):
    return repository.obter_permissao(db, permissao_id)


@router.post("/{permissao_id}/conceder/{usuario_id}", response_model=PermissaoRead)
def conceder_permissao(permissao_id: int, usuario_id: int, db: Session = Depends(get_db)):
    return repository.conceder_permissao(db, permissao_id, usuario_id)


@router.delete("/{permissao_id}/revogar/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def revogar_permissao(permissao_id: int, usuario_id: int, db: Session = Depends(get_db)):
    repository.revogar_permissao(db, permissao_id, usuario_id)
