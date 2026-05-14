from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.permissoes.model import Permissao, TipoPermissao
from src.usuarios.model import Usuario


def listar_permissoes(db: Session) -> list[Permissao]:
    return db.query(Permissao).all()


def obter_permissao(db: Session, permissao_id: int) -> Permissao:
    permissao = db.get(Permissao, permissao_id)
    if not permissao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissao nao encontrada")
    return permissao


def criar_permissao(db: Session, nome: TipoPermissao) -> Permissao:
    permissao = Permissao(nome=nome)
    db.add(permissao)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Permissao ja cadastrada")
    db.refresh(permissao)
    return permissao


def excluir_permissao(db: Session, permissao_id: int) -> None:
    permissao = obter_permissao(db, permissao_id)
    db.delete(permissao)
    db.commit()


def conceder_permissao(db: Session, permissao_id: int, usuario_id: int) -> Permissao:
    permissao = obter_permissao(db, permissao_id)
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
    if permissao in usuario.permissoes:
        raise HTTPException(status_code=409, detail="Usuario ja possui essa permissao")
    usuario.permissoes.append(permissao)
    db.commit()
    db.refresh(permissao)
    return permissao


def revogar_permissao(db: Session, permissao_id: int, usuario_id: int) -> None:
    permissao = obter_permissao(db, permissao_id)
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
    if permissao not in usuario.permissoes:
        raise HTTPException(status_code=404, detail="Usuario nao possui essa permissao")
    usuario.permissoes.remove(permissao)
    db.commit()
