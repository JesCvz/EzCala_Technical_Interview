"""
Capa de acceso a datos (repository).

NOTA PARA EL CANDIDATO: este archivo tiene la lógica de consulta a la base.
"""
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Invoice


def get_customer(db: Session, tenant_id: str, customer_id: int) -> Customer | None:
    stmt = select(Customer).where(
        Customer.id == customer_id,
        Customer.tenant_id == tenant_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_overdue_invoices(db: Session, tenant_id: str, customer_id: int) -> list[Invoice]:
    """
    Devuelve las facturas vencidas (due_date < hoy y status open) de un cliente.
    """
    stmt = select(Invoice).where(
        Invoice.tenant_id == tenant_id,            # FIX BUG 1: aislamiento por tenant
        Invoice.customer_id == customer_id,
        Invoice.due_date < date.today(),
        Invoice.status == "open",
    )
    return list(db.execute(stmt).scalars().all())


def create_invoice(db: Session, tenant_id: str, payload: dict) -> Invoice:
    """
    Inserta una factura proveniente del 'ERP'.
    """
    # FIX BUG 3: idempotencia. Si ya existe (tenant_id + netsuite_invoice_id),
    # devolvemos el existente en vez de duplicar.
    existing = db.execute(
        select(Invoice).where(
            Invoice.tenant_id == tenant_id,
            Invoice.netsuite_invoice_id == payload["netsuite_invoice_id"],
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    invoice = Invoice(
        tenant_id=tenant_id,
        netsuite_invoice_id=payload["netsuite_invoice_id"],
        customer_id=payload["customer_id"],
        amount_remaining=payload["amount_remaining"],
        currency=payload.get("currency", "MXN"),
        due_date=date.fromisoformat(payload["due_date"]),
        status=payload.get("status", "open"),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice
