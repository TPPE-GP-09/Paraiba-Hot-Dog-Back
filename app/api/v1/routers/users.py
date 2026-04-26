from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


def create_user(user_create: UserCreate, db: Session) -> UserRead:
    db_user = User(**user_create.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserRead.model_validate(db_user)


@router.post("/", response_model=UserRead)
def create_user_endpoint(
    user_create: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    return create_user(user_create, db)


