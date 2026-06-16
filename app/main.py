"""
API FastAPI del mini-EzCala.

Endpoints:
  POST /api/v1/invoices            -> ingesta de factura desde el 'ERP'
  GET  /api/v1/customers/{id}/overdue -> facturas vencidas del cliente

El tenant se resuelve desde el header X-Tenant-Id (simplificación del JWT real).
"""
import time
from fastapi import FastAPI, Header, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, init_db
from app import repository

app = FastAPI(title="mini-EzCala")


@app.on_event("startup")
def startup():
    init_db()


def tenant_from_header(x_tenant_id: str | None = Header(default=None)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=401, detail="Falta X-Tenant-Id")
    return x_tenant_id


@app.post("/api/v1/invoices")
async def ingest_invoice(
    payload: dict,
    tenant_id: str = Depends(tenant_from_header),
    db: Session = Depends(get_db),
):
    invoice = repository.create_invoice(db, tenant_id, payload)
    return {"id": invoice.id, "netsuite_invoice_id": invoice.netsuite_invoice_id}


@app.get("/api/v1/customers/{customer_id}/overdue")
async def overdue_invoices(
    customer_id: int,
    tenant_id: str = Depends(tenant_from_header),
    db: Session = Depends(get_db),
):
    customer = repository.get_customer(db, tenant_id, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer no encontrado")

    # BUG 2 (plantado): se llama una función bloqueante (time.sleep, simulando
    # una llamada lenta a NetSuite) dentro de un endpoint async, SIN await ni
    # run_in_executor. Esto bloquea el event loop y tira el throughput de toda
    # la app, no solo de esta request. Debería ser un endpoint sync, o usar
    # await anyio.to_thread / run_in_executor, o un cliente async real.
    _simulated_blocking_netsuite_call()

    invoices = repository.get_overdue_invoices(db, tenant_id, customer_id)
    return [
        {
            "id": inv.id,
            "netsuite_invoice_id": inv.netsuite_invoice_id,
            "amount_remaining": float(inv.amount_remaining),
            "currency": inv.currency,
            "due_date": inv.due_date.isoformat(),
        }
        for inv in invoices
    ]


def _simulated_blocking_netsuite_call():
    """Simula latencia de NetSuite con una llamada bloqueante."""
    time.sleep(2)
