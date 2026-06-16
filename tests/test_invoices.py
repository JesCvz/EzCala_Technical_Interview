"""
Suite de pruebas del mini-EzCala.

El candidato debe correr `pytest` y verá un test fallando.
Ese test es la PUERTA DE ENTRADA al bug de aislamiento por tenant.
Los otros dos bugs (async bloqueante e idempotencia) NO tienen test:
queremos ver si el candidato los detecta por iniciativa propia.
"""
from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Customer, Invoice
from app import repository


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()

    today = date.today()
    a = Customer(tenant_id="tenant_A", netsuite_customer_id="NS-100", name="A")
    b = Customer(tenant_id="tenant_B", netsuite_customer_id="NS-100", name="B")
    s.add_all([a, b])
    s.flush()
    s.add_all([
        Invoice(tenant_id="tenant_A", netsuite_invoice_id="A1", customer_id=a.id,
                amount_remaining=100, due_date=today - timedelta(days=5), status="open"),
        Invoice(tenant_id="tenant_B", netsuite_invoice_id="B1", customer_id=b.id,
                amount_remaining=200, due_date=today - timedelta(days=5), status="open"),
    ])
    s.commit()
    yield s
    s.close()


def test_overdue_returns_open_overdue_invoices(db):
    a = db.query(Customer).filter_by(tenant_id="tenant_A").one()
    result = repository.get_overdue_invoices(db, "tenant_A", a.id)
    assert len(result) == 1
    assert result[0].netsuite_invoice_id == "A1"


def test_no_cross_tenant_leakage(db):
    """
    Pedir las facturas vencidas del customer de tenant_B usando tenant_A
    NO debe devolver nada. Si el filtro tenant_id falta, este test truena
    y delata la fuga cross-tenant.
    """
    b = db.query(Customer).filter_by(tenant_id="tenant_B").one()
    # Un usuario de tenant_A intenta leer datos asociados al customer de tenant_B
    result = repository.get_overdue_invoices(db, "tenant_A", b.id)
    assert result == [], "FUGA CROSS-TENANT: tenant_A pudo ver facturas de tenant_B"
