from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .schemas import StatementGenerateRequest, StatementRead
from .service import generate_statement, get_statement, list_statements


router = APIRouter(prefix="/statements", tags=["statements"])


@router.get("", response_model=list[StatementRead])
def statements(
    account_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("statements:read")),
):
    return list_statements(db, user, account_id)


@router.post("/generate", response_model=StatementRead, status_code=201)
def generate(
    payload: StatementGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("statements:generate")),
):
    return generate_statement(db, user, payload)


@router.get("/{statement_id}", response_model=StatementRead)
def statement(statement_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("statements:read"))):
    return get_statement(db, user, statement_id)
