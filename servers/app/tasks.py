from celery import Celery
from .config import get_settings
from .database import SessionLocal


settings = get_settings()
celery_app = Celery("banking_platform", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task
def generate_report_job(user_id: int, report_type: str) -> dict:
    return {"user_id": user_id, "report_type": report_type, "status": "queued"}


@celery_app.task
def post_due_scheduled_transfers_job() -> dict:
    from .transfers.service import post_due_scheduled_transfers

    db = SessionLocal()
    try:
        return post_due_scheduled_transfers(db)
    finally:
        db.close()


@celery_app.task
def expire_stale_holds_job() -> dict:
    from .ledger.service import expire_stale_holds

    db = SessionLocal()
    try:
        return expire_stale_holds(db)
    finally:
        db.close()
