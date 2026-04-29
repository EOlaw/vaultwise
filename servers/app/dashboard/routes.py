from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .service import dashboard_data


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(require_permission("dashboard:read"))):
    return dashboard_data(db, user.id)
