# Documentación de la API

Base URL local: `http://localhost:8001`

Swagger interactivo: http://localhost:8001/docs

## Autenticación

Demo local **sin auth**. En producción se agregaría API Key / OAuth2 / mTLS.

## Endpoints

### `GET /health`

Verifica que la API está viva.

**Respuesta 200**

```json
{ "status": "ok" }
```

---

### `POST /api/v1/orders`

Recibe una orden externa, la valida, evita duplicados y crea `sale.order` en Odoo.

**Body**

```json
{
  "external_order_id": "EXT-1007",
  "customer": {
    "name": "Distribuidora Andina",
    "email": "compras@andina.example",
    "vat": "900123456"
  },
  "lines": [
    {
      "sku": "PROD-001",
      "quantity": 2,
      "price": 15000
    }
  ]
}
```

**Validaciones**

| Campo | Regla |
|-------|--------|
| `external_order_id` | obligatorio, único si ya está `created` |
| `customer.name` | no vacío |
| `customer.email` | email válido |
| `lines` | al menos 1 |
| `quantity` | > 0 |
| `price` | >= 0 |
| SKU | debe existir en Odoo (`default_code`) |

**Respuestas**

| Código | Significado |
|--------|-------------|
| 200 | Orden creada (o reprocesada desde `failed`) |
| 409 | Ya existía con éxito (`duplicate`) |
| 422 | Validación / productos faltantes / error Odoo |
| 500 | Error inesperado |

**Ejemplo 200**

```json
{
  "external_order_id": "EXT-1007",
  "status": "created",
  "odoo_sale_order_id": 2,
  "odoo_sale_order_name": "S00002",
  "error_message": null,
  "duplicate": false
}
```

**Ejemplo 409 (duplicado)**

```json
{
  "detail": {
    "message": "Orden externa ya procesada",
    "order": {
      "external_order_id": "EXT-1007",
      "status": "created",
      "odoo_sale_order_id": 2,
      "odoo_sale_order_name": "S00002",
      "error_message": null,
      "duplicate": true
    }
  }
}
```

---

### `GET /api/v1/orders/{external_order_id}`

Consulta el estado de procesamiento de una orden externa.

**Respuesta 200** — mismo shape que `OrderStatusOut`  
**Respuesta 404** — no existe en la base de integración

---

### `GET /api/v1/orders/{external_order_id}/logs`

Devuelve la trazabilidad ordenada de intentos/pasos.

**Ejemplo**

```json
[
  {
    "step": "received",
    "level": "info",
    "message": "Orden externa recibida",
    "created_at": "2026-08-01T..."
  },
  {
    "step": "create_order",
    "level": "info",
    "message": "Orden de venta creada en Odoo: S00001",
    "created_at": "2026-08-01T..."
  }
]
```

Pasos típicos: `received`, `validate`, `find_customer` / `create_customer`,
`check_products`, `create_order`, `duplicate_check`, `retry`, `processing_error`.

---

### `GET /api/v1/orders/stats/summary`

Resumen de cuántas órdenes hay por `status`.

**Respuesta 200**

```json
{
  "by_status": {
    "created": 3,
    "failed": 1
  },
  "total": 4
}
```

---

### `GET /debug/odoo-config`

Solo para demo/local: muestra URL/DB/usuario Odoo (sin password).

## Códigos de estado de negocio (`status`)

| status | Significado |
|--------|-------------|
| `received` | Recibida / en reintento |
| `validating` | Conectando / validando contra Odoo |
| `created` | `sale.order` creada en Odoo |
| `failed` | Error; se puede reintentar con el mismo `external_order_id` |

## Ejemplo curl

```powershell
curl -X POST http://localhost:8001/api/v1/orders `
  -H "Content-Type: application/json" `
  -d "{\"external_order_id\":\"EXT-1007\",\"customer\":{\"name\":\"Andina\",\"email\":\"compras@andina.example\"},\"lines\":[{\"sku\":\"PROD-001\",\"quantity\":1,\"price\":10000}]}"
```
