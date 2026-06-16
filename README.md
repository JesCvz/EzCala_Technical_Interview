# mini-EzCala — Ejercicio técnico

Slice mínimo del proyecto real: ingesta de facturas desde un "ERP" y consulta
de facturas vencidas por cliente, con aislamiento por `tenant_id`.

## Opción A — GitHub Codespaces (recomendado, sin instalar nada)
1. En el repo de GitHub: botón verde **Code** → pestaña **Codespaces** → **Create codespace**.
2. Espera a que termine el setup (instala dependencias y carga datos solo).
3. En la terminal del Codespace:
   ```bash
   make run
   ```
4. Cuando aparezca el aviso del puerto 8000, ábrelo. Para la vista, abre `frontend/index.html`.

## Opción B — Local
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
make setup
make seed
make run
```

## Pruebas
```bash
make test    # o: pytest -v
```

## Endpoints
- `POST /api/v1/invoices` — ingesta. Header `X-Tenant-Id`. Body JSON de factura.
- `GET  /api/v1/customers/{id}/overdue` — facturas vencidas. Header `X-Tenant-Id`.

## Tu tarea
El entrevistador te la explica en vivo. Trabaja pensando en voz alta.
