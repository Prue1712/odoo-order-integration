import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import IntegrationLog, ProcessedOrder


def get_order_by_external_id(db: Session, external_order_id: str) -> ProcessedOrder | None:
    return (
        db.query(ProcessedOrder)
        .filter(ProcessedOrder.external_order_id == external_order_id)
        .first()
    )


def create_order(
    db: Session,
    *,
    external_order_id: str,
    customer_email: str,
    payload: dict[str, Any],
    status: str = "received",
) -> ProcessedOrder:
    order = ProcessedOrder(
        external_order_id=external_order_id,
        status=status,
        customer_email=customer_email,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def update_order(
    db: Session,
    order: ProcessedOrder,
    *,
    status: str | None = None,
    odoo_sale_order_id: int | None = None,
    odoo_sale_order_name: str | None = None,
    error_message: str | None = None,
) -> ProcessedOrder:
    if status is not None:
        order.status = status
    if odoo_sale_order_id is not None:
        order.odoo_sale_order_id = odoo_sale_order_id
    if odoo_sale_order_name is not None:
        order.odoo_sale_order_name = odoo_sale_order_name
    if error_message is not None:
        order.error_message = error_message
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def add_log(
    db: Session,
    *,
    external_order_id: str,
    step: str,
    message: str,
    level: str = "info",
    details: dict[str, Any] | None = None,
) -> IntegrationLog:
    log = IntegrationLog(
        external_order_id=external_order_id,
        step=step,
        level=level,
        message=message,
        details_json=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_logs(db: Session, external_order_id: str) -> list[IntegrationLog]:
    return (
        db.query(IntegrationLog)
        .filter(IntegrationLog.external_order_id == external_order_id)
        .order_by(IntegrationLog.id.asc())
        .all()
    )


def count_orders_by_status(db: Session) -> dict[str, int]:
    """Cuenta órdenes por status (útil para monitoreo / demo)."""
    from sqlalchemy import func

    rows = (
        db.query(ProcessedOrder.status, func.count(ProcessedOrder.id))
        .group_by(ProcessedOrder.status)
        .all()
    )
    return {status: int(total) for status, total in rows}
