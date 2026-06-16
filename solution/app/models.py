"""
Modelos de datos del mini-EzCala.
Capa de persistencia: SQLAlchemy 2.0 + SQLite (para que corra sin infra).
"""
from datetime import date
from sqlalchemy import String, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    netsuite_customer_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="customer")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    netsuite_invoice_id: Mapped[str] = mapped_column(String, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    amount_remaining: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="MXN")
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")

    customer: Mapped["Customer"] = relationship(back_populates="invoices")
