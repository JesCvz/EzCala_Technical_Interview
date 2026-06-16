# mini-EzCala — Ejercicio técnico

Slice mínimo del proyecto real: ingesta de facturas desde un "ERP" y consulta
de facturas vencidas por cliente, con aislamiento por `tenant_id`.

## Setup (5 min)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed_data        # carga datos mock (tenant_A y tenant_B)
uvicorn app.main:app --reload  # levanta la API en http://localhost:8000
```
Abre `frontend/index.html` en el navegador para la vista.

## Pruebas
```bash
pytest -v
```

## Endpoints
- `POST /api/v1/invoices` — ingesta. Header `X-Tenant-Id`. Body JSON de factura.
- `GET  /api/v1/customers/{id}/overdue` — facturas vencidas. Header `X-Tenant-Id`.

## Tu tarea
El entrevistador te la explica en vivo. Trabaja pensando en voz alta.
