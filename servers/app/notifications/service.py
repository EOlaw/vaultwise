import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..iam.models import Role, UserRoleAssignment
from ..organizations.models import AccountEntitlement, EntitlementStatus, MembershipRole, MembershipStatus, OrganizationMembership
from ..transfers.models import Transfer
from ..users.models import User
from .models import Notification, NotificationPriority, NotificationType


def create_notification(
    db: Session,
    *,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    body: str,
    organization_id: int | None = None,
    priority: NotificationPriority = NotificationPriority.info,
    action_url: str | None = None,
    metadata: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        organization_id=organization_id,
        notification_type=notification_type,
        priority=priority,
        title=title,
        body=body,
        action_url=action_url,
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    )
    db.add(notification)
    return notification


def list_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        query = query.where(Notification.read_at.is_(None))
    return db.scalars(query.order_by(Notification.created_at.desc(), Notification.id.desc()).limit(200)).all()


def mark_notification_read(db: Session, user: User, notification_id: int) -> Notification:
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if not notification:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notification.read_at = notification.read_at or datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, user: User) -> int:
    notifications = db.scalars(select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))).all()
    now = datetime.utcnow()
    for notification in notifications:
        notification.read_at = now
    db.commit()
    return len(notifications)


def _transfer_approver_user_ids(db: Session, transfer: Transfer) -> set[int]:
    if transfer.organization_id is None:
        return set()
    membership_user_ids = set(
        db.scalars(
            select(OrganizationMembership.user_id).where(
                OrganizationMembership.organization_id == transfer.organization_id,
                OrganizationMembership.status == MembershipStatus.active,
                OrganizationMembership.role.in_([MembershipRole.owner, MembershipRole.admin, MembershipRole.approver]),
            )
        ).all()
    )
    entitled_user_ids = set(
        db.scalars(
            select(AccountEntitlement.user_id).where(
                AccountEntitlement.organization_id == transfer.organization_id,
                AccountEntitlement.account_id == transfer.from_account_id,
                AccountEntitlement.status == EntitlementStatus.active,
                AccountEntitlement.can_approve.is_(True),
            )
        ).all()
    )
    return membership_user_ids & entitled_user_ids


def notify_transfer_pending_approval(db: Session, transfer: Transfer) -> None:
    create_notification(
        db,
        user_id=transfer.created_by_user_id,
        organization_id=transfer.organization_id,
        notification_type=NotificationType.transfer,
        priority=NotificationPriority.action_required,
        title="Transfer pending approval",
        body=f"Transfer #{transfer.id} for {transfer.amount} {transfer.currency} is waiting for approval.",
        action_url=f"/transfers/{transfer.id}",
        metadata={"transfer_id": transfer.id},
    )
    for user_id in _transfer_approver_user_ids(db, transfer) - {transfer.created_by_user_id}:
        create_notification(
            db,
            user_id=user_id,
            organization_id=transfer.organization_id,
            notification_type=NotificationType.approval,
            priority=NotificationPriority.action_required,
            title="Approval requested",
            body=f"Transfer #{transfer.id} needs your approval.",
            action_url="/approvals",
            metadata={"transfer_id": transfer.id},
        )


def notify_transfer_posted(db: Session, transfer: Transfer) -> None:
    create_notification(
        db,
        user_id=transfer.created_by_user_id,
        organization_id=transfer.organization_id,
        notification_type=NotificationType.transfer,
        priority=NotificationPriority.info,
        title="Transfer posted",
        body=f"Transfer #{transfer.id} posted for {transfer.amount} {transfer.currency}.",
        action_url=f"/transfers/{transfer.id}",
        metadata={"transfer_id": transfer.id},
    )


def notify_transfer_rejected(db: Session, transfer: Transfer, notes: str | None = None) -> None:
    create_notification(
        db,
        user_id=transfer.created_by_user_id,
        organization_id=transfer.organization_id,
        notification_type=NotificationType.approval,
        priority=NotificationPriority.warning,
        title="Transfer rejected",
        body=f"Transfer #{transfer.id} was rejected." + (f" {notes}" if notes else ""),
        action_url=f"/transfers/{transfer.id}",
        metadata={"transfer_id": transfer.id},
    )


def risk_staff_user_ids(db: Session) -> set[int]:
    rows = db.execute(
        select(UserRoleAssignment.user_id)
        .join(Role, Role.id == UserRoleAssignment.role_id)
        .where(Role.name.in_(["super_admin", "bank_admin", "risk_manager", "compliance_officer"]))
    ).all()
    return {row[0] for row in rows}


def notify_risk_alert_created(db: Session, *, alert_id: int, title: str, severity: str, organization_id: int | None = None) -> None:
    priority = NotificationPriority.critical if severity in {"high", "critical"} else NotificationPriority.warning
    for user_id in risk_staff_user_ids(db):
        create_notification(
            db,
            user_id=user_id,
            organization_id=organization_id,
            notification_type=NotificationType.risk,
            priority=priority,
            title="Risk alert opened",
            body=f"{title} ({severity})",
            action_url="/risk/alerts",
            metadata={"alert_id": alert_id},
        )


def notify_statement_generated(db: Session, *, user_id: int, account_id: int, statement_id: int, organization_id: int | None = None) -> None:
    create_notification(
        db,
        user_id=user_id,
        organization_id=organization_id,
        notification_type=NotificationType.statement,
        priority=NotificationPriority.info,
        title="Statement generated",
        body=f"Statement #{statement_id} is available for account #{account_id}.",
        action_url=f"/statements/{statement_id}",
        metadata={"account_id": account_id, "statement_id": statement_id},
    )
