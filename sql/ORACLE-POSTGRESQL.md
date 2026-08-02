# Nota Oracle ↔ PostgreSQL

## Contexto

En esta prueba la trazabilidad vive en **PostgreSQL** (`integration`, puerto 5433).
Si en un escenario real existiera una fuente en **Oracle** (por ejemplo un ERP legacy
o un data warehouse), el análisis no se reescribe desde cero: se **alinea por claves
de negocio** y se sincroniza hacia un modelo comparable en PostgreSQL.

## Principio clave

No compares por IDs internos (`sale.order.id` de Odoo vs `ORDER_ID` de Oracle).
Compara por **clave de negocio**:

- `external_order_id`
- email / VAT del cliente
- SKU del producto
- fecha de negocio del pedido

Los IDs internos son locales a cada sistema.

## Enfoque recomendado (staging + comparación)

1. **Extraer** de Oracle las órdenes relevantes a tablas staging en PostgreSQL  
   (ETL programado, dump, o CDC si hay volumen alto).
2. **Normalizar** tipos y zonas horarias (Oracle `DATE`/`TIMESTAMP` → `timestamptz`).
3. **Comparar** con `processed_orders` / `integration_logs` por `external_order_id`.
4. **Reportar** diferencias: solo en Oracle, solo en Postgres, o campos distintos.

Ejemplo conceptual de comparación (tras cargar staging):

```sql
-- staging.oracle_orders (cargada desde Oracle)
-- processed_orders      (nuestra integración)

SELECT
    COALESCE(o.external_order_id, p.external_order_id) AS external_order_id,
    CASE
        WHEN o.external_order_id IS NULL THEN 'solo_postgres'
        WHEN p.external_order_id IS NULL THEN 'solo_oracle'
        WHEN o.amount <> p.amount_proxy THEN 'monto_diferente'
        ELSE 'ok'
    END AS resultado
FROM staging.oracle_orders o
FULL OUTER JOIN processed_orders p
    ON p.external_order_id = o.external_order_id;
```

## Cómo adaptarías el análisis SQL de este repo

| Consulta actual (Postgres) | Adaptación con Oracle |
|----------------------------|------------------------|
| Órdenes por `status` | Misma lógica sobre staging Oracle + join a `processed_orders` |
| Timeline en `integration_logs` | Se mantiene en Postgres; Oracle aporta el “sistema origen” |
| Fallidos / reintentos | Cruza fallos de integración vs órdenes que Oracle cree “enviadas” |
| Clientes activos | Une por email/VAT normalizado (trim, lower, formato VAT) |

## Opciones de sincronización

| Opción | Cuándo usarla |
|--------|----------------|
| ETL batch (noche / cada hora) | Volumen moderado, latencia aceptable |
| CDC (cambio de datos) | Casi tiempo real, alto volumen |
| Vista materializada / réplica de lectura | Reportes pesados sin pegarle a Oracle productivo |
| API bidireccional | Solo si Oracle expone servicios confiables |

En upsert hacia PostgreSQL se usa la semántica de `ON CONFLICT (external_order_id) DO UPDATE`
(equivalente conceptual al `MERGE` de Oracle).

## Qué NO haría

- Duplicar toda la base de Odoo en Oracle “porque sí”.
- Usar el ID numérico de Odoo como PK en Oracle.
- Analizar sin una tabla de mapeo (`external_order_id` ↔ ids locales).

## Resumen para la entrevista (30 segundos)

> “Si hubiera Oracle, traería las órdenes a un staging en PostgreSQL y compararía
> por `external_order_id`. La trazabilidad de la integración se queda en Postgres;
> Oracle es fuente de verdad del origen. Diferencias se detectan con FULL OUTER JOIN
> o con un job ETL + MERGE/upsert.”
