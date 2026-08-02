# AGENTS.md — guía para agentes / desarrolladores

Este documento permite a una persona o a una IA **entender, operar y extender**
la solución sin redescubrir el diseño.

## Propósito del proyecto

Middleware en **Python (FastAPI)** que:

1. Recibe pedidos de un sistema externo vía API REST.
2. Valida datos y evita duplicados por `external_order_id`.
3. Integra con **Odoo 18** por XML-RPC (clientes, productos, `sale.order`).
4. Persiste trazabilidad en **PostgreSQL** propio (puerto 5433).

No es un módulo Odoo. Es una capa de integración al lado de Odoo.

## Mapa del repositorio

```text
app/
  main.py                 # FastAPI app + /health
  config.py               # Settings desde .env
  api/routes_orders.py    # Endpoints de órdenes
  schemas/order.py        # Validación Pydantic (entrada/salida)
  services/
    order_processor.py    # Orquestación de negocio (aquí está el flujo)
    odoo_client.py        # XML-RPC hacia Odoo
  db/
    models.py             # processed_orders, integration_logs
    repository.py         # Acceso a datos
    session.py            # Engine / Session / init_db
docs/
  API.md                  # Contrato HTTP
  diagram.md              # Flujo + ER
sql/
  queries.sql             # Análisis
  ORACLE-POSTGRESQL.md    # Adaptación Oracle
docker-compose.yml        # Odoo 18 + 2 Postgres
.env.example              # Plantilla de configuración
EJERCICIOS-ENTREVISTA.txt # Ensayo oral
BITACORA-ESTUDIO.txt      # Notas de aprendizaje
```

## Arranque local (checklist)

1. Docker Desktop en verde.
2. `docker compose up -d` → Odoo `:8069`, Odoo DB `:5432`, integración `:5433`.
3. Primera vez: crear BD `odoo18` en Odoo e instalar app **Ventas**.
4. Crear producto con `default_code` / Referencia interna = SKU usado en demos (ej. `PROD-001`).
5. Copiar `.env.example` → `.env` y ajustar `ODOO_PASSWORD` / `ODOO_DB`.
6. `python -m venv .venv` → activar → `pip install -r requirements.txt`.
7. `uvicorn app.main:app --reload --port 8001`
8. Probar en http://localhost:8001/docs

## Decisiones de arquitectura (no las cambies sin motivo)

| Decisión | Motivo |
|----------|--------|
| Middleware fuera de Odoo | Idempotencia, logs y demo claros sin custom module |
| XML-RPC | Estándar Odoo, simple para la prueba |
| Dos Postgres | Separar datos de Odoo vs trazabilidad de integración |
| `client_order_ref` | Guardar ID externo visible en la orden de venta |
| Reintento solo si `failed` | Si `created`, nunca duplicar `sale.order` |
| HTTP 409 en duplicado | Deja explícito el anti-duplicado ante el cliente API |

## Dónde tocar para cambios frecuentes

| Pedido | Archivo(s) |
|--------|------------|
| Cambiar reglas de validación (precio, qty) | `app/schemas/order.py` |
| Buscar cliente por VAT además de email | `app/services/odoo_client.py`, `order_processor.py` |
| Confirmar orden automáticamente | `odoo_client.create_sale_order` (+ `action_confirm`) |
| Nuevo endpoint de estadísticas | Ya existe `GET /api/v1/orders/stats/summary` (`routes_orders.py` + `repository.count_orders_by_status`) |
| Campos nuevos en trazabilidad | `models.py` (+ migración / recreate) |
| Credenciales | `.env` (nunca commitear) |

## Estados de `processed_orders.status`

`received` → `validating` → `created` | `failed`

- `created`: terminal de éxito (bloquea duplicados).
- `failed`: permite reintento con el mismo `external_order_id`.

## Contratos importantes

- Clave de negocio: **`external_order_id`** (única en éxito).
- SKU Odoo: campo **`default_code`** del producto.
- Cliente: búsqueda por **email**; creación con name/email/vat opcional.
- Logs: tabla `integration_logs` ligada lógicamente por `external_order_id`.

## Pruebas manuales mínimas

1. POST orden válida → `status=created` y aparece en Odoo Ventas.
2. POST mismo ID → 409 duplicate.
3. POST con SKU inexistente → 422 / `failed` + log `check_products`.
4. GET `/orders/{id}` y `/logs` → estado y timeline.
5. Ejecutar 2–3 queries de `sql/queries.sql`.

## Extensiones naturales (producción)

- Auth en la API (API key).
- Cola (Redis/RQ/Celery) + reintentos con backoff.
- Módulo Odoo custom si se necesita UI/campo dedicado.
- Tests automatizados (pytest + httpx + mock XML-RPC).
- Observabilidad (OpenTelemetry / Sentry).

## Convenciones para agentes de código

- No inventar endpoints que no existan; mira `routes_orders.py`.
- No mezclar la DB de Odoo (`:5432`) con la de integración (`:5433`).
- Preferir cambios pequeños y localizados; el orquestador es `order_processor.py`.
- Mantener docs (`README`, `docs/API.md`, este archivo) alineados con el código.
- Español en documentación de entrega; código/identificadores en inglés.
