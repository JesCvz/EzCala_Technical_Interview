"""
Carga de datos mock simulando un volcado del 'ERP'.
Crea DOS tenants a propósito: así el candidato puede verificar el
aislamiento por tenant (y detectar el cross-tenant leakage).

Uso:
    python -m app.seed_data
"""
from datetime import date, timedelta
from app.db import SessionLocal, init_db
from app.models import Customer, Invoice


def run():
    init_db()
    db = SessionLocal()

    # Limpieza simple para reruns
    db.query(Invoice).delete()
    db.query(Customer).delete()
    db.commit()

    today = date.today()

    # --- Tenant A ---
    cust_a = Customer(tenant_id="tenant_A", netsuite_customer_id="NS-CUST-100", name="Aceros del Norte")
    db.add(cust_a)
    db.flush()
    db.add_all([
        Invoice(tenant_id="tenant_A", netsuite_invoice_id="NS-INV-A1",
                customer_id=cust_a.id, amount_remaining=15000, currency="MXN",
                due_date=today - timedelta(days=10), status="open"),   # vencida
        Invoice(tenant_id="tenant_A", netsuite_invoice_id="NS-INV-A2",
                customer_id=cust_a.id, amount_remaining=8000, currency="MXN",
                due_date=today + timedelta(days=15), status="open"),   # NO vencida
        Invoice(tenant_id="tenant_A", netsuite_invoice_id="NS-INV-A3",
                customer_id=cust_a.id, amount_remaining=3000, currency="MXN",
                due_date=today - timedelta(days=40), status="paid"),   # vencida pero pagada
    ])

    # --- Tenant B (mismo customer_id lógico para evidenciar el leakage) ---
    cust_b = Customer(tenant_id="tenant_B", netsuite_customer_id="NS-CUST-100", name="Comercializadora Sur")
    db.add(cust_b)
    db.flush()
    db.add_all([
        Invoice(tenant_id="tenant_B", netsuite_invoice_id="NS-INV-B1",
                customer_id=cust_b.id, amount_remaining=99999, currency="USD",
                due_date=today - timedelta(days=5), status="open"),    # vencida (de OTRO tenant)
    ])

    db.commit()
    print(f"Seed listo. Customer A id={cust_a.id} (tenant_A), Customer B id={cust_b.id} (tenant_B)")
    db.close()


if __name__ == "__main__":
    run()
