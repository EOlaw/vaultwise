from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user, require_permission
from .models import User
from .schemas import UserRead, UserUpdate
from .service import update_user


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_permission("users:read"))):
    return db.scalars(select(User).order_by(User.created_at.desc())).all()


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_permission("users:update"))):
    return update_user(db, db.get(User, user_id), payload)
