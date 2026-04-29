import csv
import io
from datetime import date
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..accounts.service import accessible_account_ids
from ..dashboard.service import dashboard_data
from ..database import get_db
from ..dependencies import require_permission
from ..transactions.models import Transaction
from ..users.models import User


router = APIRouter(prefix="/reports", tags=["reports"])


def _pdf_escape(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(title: str, lines: list[str]) -> bytes:
    text_commands = ["BT", "/F1 16 Tf", "72 760 Td", f"({_pdf_escape(title)}) Tj", "/F1 10 Tf", "0 -24 Td"]
    for line in lines[:42]:
        text_commands.append(f"({_pdf_escape(line)}) Tj")
        text_commands.append("0 -14 Td")
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = io.BytesIO()
    output.write(b"%PDF-1.4\n")
    offsets: list[int] = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(output.tell())
        output.write(f"{index} 0 obj\n".encode("ascii"))
        output.write(obj)
        output.write(b"\nendobj\n")
    xref_offset = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.write(f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return output.getvalue()


@router.get("/monthly/{month}")
def monthly_report(month: str, db: Session = Depends(get_db), user: User = Depends(require_permission("reports:read"))):
    data = dashboard_data(db, user.id)
    data["monthly_cash_flow"] = [row for row in data["monthly_cash_flow"] if row["month"] == month]
    return data


@router.get("/yearly/{year}")
def yearly_report(year: int, db: Session = Depends(get_db), user: User = Depends(require_permission("reports:read"))):
    data = dashboard_data(db, user.id)
    data["monthly_cash_flow"] = [row for row in data["monthly_cash_flow"] if row["month"].startswith(str(year))]
    return data


@router.get("/category/{category}")
def category_report(category: str, db: Session = Depends(get_db), user: User = Depends(require_permission("reports:read"))):
    account_ids = accessible_account_ids(db, user.id)
    rows = db.scalars(select(Transaction).where(Transaction.account_id.in_(account_ids), Transaction.category == category)).all() if account_ids else []
    return {"category": category, "transactions": rows, "total": round(sum(float(row.amount) for row in rows), 2)}


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db), user: User = Depends(require_permission("reports:export"))):
    account_ids = accessible_account_ids(db, user.id)
    transactions = db.scalars(select(Transaction).where(Transaction.account_id.in_(account_ids)).order_by(Transaction.occurred_on.desc())).all() if account_ids else []
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "type", "category", "amount", "tags", "notes"])
    for transaction in transactions:
        writer.writerow([transaction.occurred_on, transaction.type.value, transaction.category, transaction.amount, transaction.tags, transaction.notes])
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=transactions.csv"})


@router.get("/export.pdf")
def export_pdf(db: Session = Depends(get_db), user: User = Depends(require_permission("reports:export"))):
    data = dashboard_data(db, user.id)
    summary = data["summary"]
    lines = [
        f"Generated: {date.today().isoformat()}",
        f"User: {user.email}",
        "",
        "Financial Summary",
        f"Net worth: {summary.get('net_worth')}",
        f"Total income: {summary.get('total_income')}",
        f"Total expenses: {summary.get('total_expenses')}",
        f"Net cash flow: {summary.get('net_cash_flow')}",
        "",
        "Monthly Cash Flow",
    ]
    for row in data.get("monthly_cash_flow", [])[-12:]:
        lines.append(f"{row['month']}: income {row['income']} / expenses {row['expenses']} / net {row['net']}")
    pdf = _simple_pdf("BankOS Financial Report", lines)
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=financial-report.pdf"},
    )
