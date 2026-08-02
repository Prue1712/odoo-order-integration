-- =============================================================================
-- Consultas SQL de análisis — base de integración (puerto 5433)
-- Base: integration / usuario: integration
-- Conectar (psql o DBeaver):
--   host=localhost port=5433 dbname=integration user=integration password=integration
-- =============================================================================

-- 1) Resumen de órdenes por estado
SELECT
    status,
    COUNT(*) AS total,
    COUNT(odoo_sale_order_id) AS con_orden_odoo
FROM processed_orders
GROUP BY status
ORDER BY total DESC;

-- 2) Órdenes creadas con éxito (trazabilidad negocio ↔ Odoo)
SELECT
    external_order_id,
    odoo_sale_order_id,
    odoo_sale_order_name,
    customer_email,
    created_at,
    updated_at
FROM processed_orders
WHERE status = 'created'
ORDER BY created_at DESC;

-- 3) Órdenes fallidas (para soporte / reintento)
SELECT
    external_order_id,
    customer_email,
    error_message,
    created_at,
    updated_at
FROM processed_orders
WHERE status = 'failed'
ORDER BY updated_at DESC;

-- 4) Timeline de una orden externa (cambiar el ID)
SELECT
    created_at,
    step,
    level,
    message
FROM integration_logs
WHERE external_order_id = 'EXT-1006'
ORDER BY created_at ASC, id ASC;

-- 5) Intentos con error por paso (dónde falla más la integración)
SELECT
    step,
    COUNT(*) AS errores
FROM integration_logs
WHERE level = 'error'
GROUP BY step
ORDER BY errores DESC;

-- 6) Clientes más activos (por email en órdenes procesadas)
SELECT
    customer_email,
    COUNT(*) AS ordenes,
    SUM(CASE WHEN status = 'created' THEN 1 ELSE 0 END) AS exitosas,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS fallidas
FROM processed_orders
WHERE customer_email IS NOT NULL
GROUP BY customer_email
ORDER BY ordenes DESC;

-- 7) Tiempo aproximado de procesamiento (creación → última actualización)
SELECT
    external_order_id,
    status,
    created_at,
    updated_at,
    EXTRACT(EPOCH FROM (updated_at - created_at)) AS segundos
FROM processed_orders
WHERE status IN ('created', 'failed')
ORDER BY segundos DESC NULLS LAST
LIMIT 20;

-- 8) Duplicados intentados (logs de anti-duplicado)
SELECT
    external_order_id,
    COUNT(*) AS intentos_duplicado,
    MIN(created_at) AS primer_aviso,
    MAX(created_at) AS ultimo_aviso
FROM integration_logs
WHERE step = 'duplicate_check'
GROUP BY external_order_id
ORDER BY intentos_duplicado DESC;

-- 9) Órdenes sin logs (anomalía / datos incompletos)
SELECT po.external_order_id, po.status, po.created_at
FROM processed_orders po
LEFT JOIN integration_logs il
    ON il.external_order_id = po.external_order_id
WHERE il.id IS NULL;

-- 10) Últimas 50 entradas de trazabilidad (operación diaria)
SELECT
    id,
    created_at,
    external_order_id,
    step,
    level,
    LEFT(message, 120) AS message_preview
FROM integration_logs
ORDER BY created_at DESC, id DESC
LIMIT 50;
