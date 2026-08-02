"""Orquestador: valida, evita duplicados, habla con Odoo y deja logs."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import repository as repo
from app.db.models import ProcessedOrder
from app.schemas.order import ExternalOrderIn, OrderStatusOut
from app.services.odoo_client import OdooClient


class OrderProcessingError(Exception):
    def __init__(self, message: str, status: str = "failed") -> None:
        super().__init__(message)
        self.message = message
        self.status = status


def _to_status(order: ProcessedOrder, *, duplicate: bool = False) -> OrderStatusOut:
    return OrderStatusOut(
        external_order_id=order.external_order_id,
        status=order.status,
        odoo_sale_order_id=order.odoo_sale_order_id,
        odoo_sale_order_name=order.odoo_sale_order_name,
        error_message=order.error_message,
        duplicate=duplicate,
    )


def _run_odoo_pipeline(db: Session, order: ProcessedOrder, payload: ExternalOrderIn) -> OrderStatusOut:
    try:
        repo.update_order(db, order, status="validating")
        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="validate",
            message="Validación de esquema OK; conectando con Odoo",
        )

        odoo = OdooClient()

        partner = odoo.find_partner_by_email(str(payload.customer.email))
        if partner:
            partner_id = int(partner["id"])
            repo.add_log(
                db,
                external_order_id=payload.external_order_id,
                step="find_customer",
                message=f"Cliente existente en Odoo id={partner_id}",
                details=partner,
            )
        else:
            partner_id = odoo.create_partner(
                name=payload.customer.name,
                email=str(payload.customer.email),
                vat=payload.customer.vat,
                phone=payload.customer.phone,
                mobile=payload.customer.mobile,
                website=payload.customer.website,
                job_position=payload.customer.job_position,
                is_company=payload.customer.is_company,
            )
            repo.add_log(
                db,
                external_order_id=payload.external_order_id,
                step="create_customer",
                message=f"Cliente creado en Odoo id={partner_id}",
            )

        resolved_lines = []
        missing_skus = []
        for line in payload.lines:
            product = odoo.find_product_by_sku(line.sku)
            if not product:
                missing_skus.append(line.sku)
                continue
            resolved_lines.append(
                {
                    "product_id": int(product["id"]),
                    "quantity": line.quantity,
                    "price": line.price,
                    "sku": line.sku,
                }
            )

        if missing_skus:
            msg = f"Productos no encontrados en Odoo: {', '.join(missing_skus)}"
            repo.add_log(
                db,
                external_order_id=payload.external_order_id,
                step="check_products",
                level="error",
                message=msg,
                details={"missing_skus": missing_skus},
            )
            repo.update_order(db, order, status="failed", error_message=msg)
            raise OrderProcessingError(msg)

        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="check_products",
            message="Todos los productos existen en Odoo",
            details={"lines": resolved_lines},
        )

        sale = odoo.create_sale_order(
            partner_id=partner_id,
            lines=resolved_lines,
            external_order_id=payload.external_order_id,
        )
        repo.update_order(
            db,
            order,
            status="created",
            odoo_sale_order_id=int(sale["id"]),
            odoo_sale_order_name=sale.get("name"),
            error_message=None,
        )
        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="create_order",
            message=f"Orden de venta creada en Odoo: {sale.get('name')}",
            details=sale,
        )
        return _to_status(order)

    except OrderProcessingError:
        raise
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="processing_error",
            level="error",
            message=msg,
        )
        repo.update_order(db, order, status="failed", error_message=msg)
        raise OrderProcessingError(msg) from exc


def process_external_order(db: Session, payload: ExternalOrderIn) -> OrderStatusOut:
    existing = repo.get_order_by_external_id(db, payload.external_order_id)

    # Éxito previo → no duplicar
    if existing and existing.status == "created":
        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="duplicate_check",
            level="warning",
            message="Orden externa ya creada en Odoo; se evita duplicado",
            details={"existing_status": existing.status},
        )
        return _to_status(existing, duplicate=True)

    # Fallo previo → permitir reintento
    if existing and existing.status == "failed":
        repo.add_log(
            db,
            external_order_id=payload.external_order_id,
            step="retry",
            message="Reintento de orden previamente fallida",
        )
        repo.update_order(
            db,
            existing,
            status="received",
            error_message=None,
        )
        return _run_odoo_pipeline(db, existing, payload)

    # Primera vez
    order = repo.create_order(
        db,
        external_order_id=payload.external_order_id,
        customer_email=str(payload.customer.email),
        payload=payload.model_dump(mode="json"),
        status="received",
    )
    repo.add_log(
        db,
        external_order_id=payload.external_order_id,
        step="received",
        message="Orden externa recibida",
    )
    return _run_odoo_pipeline(db, order, payload)
