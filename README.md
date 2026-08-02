# odoo-order-integration

Solución de integración **pedidos externos → Odoo 18** con Python, SQL y APIs.

Recibe una orden por REST, valida cliente/productos/cantidades/precios, evita
duplicados, crea la orden de venta en Odoo y deja trazabilidad consultable en
PostgreSQL.

## Arquitectura (resumen)

```text
Sistema externo → FastAPI → Odoo 18 (XML-RPC)
                    ↓
           Postgres integración (:5433)
```

| Pieza | Tecnología | Puerto |
|-------|------------|--------|
| API | FastAPI + Uvicorn | 8001 |
| Odoo | `odoo:18.0` | 8069 |
| DB Odoo | PostgreSQL 16 | 5432 |
| DB integración | PostgreSQL 16 | 5433 |

Detalle visual: [docs/diagram.md](docs/diagram.md)

## Requisitos

- Docker Desktop (WSL2 en Windows)
- Python 3.11+ (se probó con 3.14)
- Git

## Instalación rápida

### 1) Clonar / entrar al repo

```powershell
cd C:\Users\danny\odoo-order-integration
```

### 2) Levantar infraestructura

```powershell
docker compose up -d
```

Espera a que `odoo_app`, `odoo_postgres` e `integration_postgres` estén Up.

### 3) Configurar Odoo (solo primera vez)

1. Abre http://localhost:8069
2. Crea la base:
   - Database Name: `odoo18`
   - Email / password: los que uses en `.env` (ej. `admin` / `admin`)
   - Demo data: desmarcado
3. Instala la app **Ventas / Sales**
4. Crea al menos un producto con **Referencia interna** = `PROD-001` (ese es el SKU)

### 4) Configurar la API

```powershell
copy .env.example .env
# Edita ODOO_DB / ODOO_USER / ODOO_PASSWORD si hace falta
```

### 5) Entorno Python y arranque

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

- Swagger: http://localhost:8001/docs  
- Health: http://localhost:8001/health  

## Demo en 2 minutos

1. En Swagger, `POST /api/v1/orders` con:

```json
{
  "external_order_id": "EXT-1007",
  "customer": {
    "name": "Distribuidora Andina",
    "email": "compras@andina.example",
    "vat": "900123456"
  },
  "lines": [
    { "sku": "PROD-001", "quantity": 2, "price": 15000 }
  ]
}
```

2. Verifica en Odoo → **Ventas → Órdenes** (referencia `EXT-1007`).
3. `GET /api/v1/orders/EXT-1007` y `.../logs`.
4. Repite el mismo POST → **409** (anti-duplicado).

## Documentación de entrega

| Entregable | Archivo |
|------------|---------|
| API | [docs/API.md](docs/API.md) |
| Diagrama lógico + ER | [docs/diagram.md](docs/diagram.md) |
| Consultas SQL | [sql/queries.sql](sql/queries.sql) |
| Nota Oracle ↔ PostgreSQL | [sql/ORACLE-POSTGRESQL.md](sql/ORACLE-POSTGRESQL.md) |
| Guía para IA / extensión | [AGENTS.md](AGENTS.md) |
| Uso de IA (puntos adicionales) | [SKILLS.md](SKILLS.md) |

## Validaciones cubiertas

- Identificador externo obligatorio
- Cliente con nombre + email (+ VAT opcional)
- Productos existentes en Odoo (SKU)
- Cantidades > 0 y precios >= 0
- Órdenes duplicadas (mismo `external_order_id` si ya `created`)
- Errores registrados en `integration_logs` + `error_message`

## SQL rápido

Con DBeaver/psql a `localhost:5433` (user/pass/db: `integration`):

```sql
SELECT status, COUNT(*) FROM processed_orders GROUP BY status;
```

Más consultas en `sql/queries.sql`.

## Estructura del código

- `app/api` — HTTP
- `app/schemas` — validación
- `app/services/order_processor.py` — orquestación
- `app/services/odoo_client.py` — XML-RPC
- `app/db` — modelos y repositorio de trazabilidad

## Parar / limpiar

```powershell
docker compose stop
# o borrar contenedores (conserva volúmenes):
docker compose down
```

## Licencia / uso

Prueba técnica educativa — adaptar credenciales antes de cualquier entorno real.
