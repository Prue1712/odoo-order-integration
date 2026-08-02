from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import repository as repo
from app.db.session import get_db
from app.schemas.order import ExternalOrderIn, IntegrationLogOut, OrderStatusOut
from app.services.order_processor import OrderProcessingError, process_external_order

router = APIRouter(prefix="/api/v1", tags=["orders"])


@router.post("/orders", response_model=OrderStatusOut)
def create_order(payload: ExternalOrderIn, db: Session = Depends(get_db)) -> OrderStatusOut:
    """
    Recibe una orden externa, la valida, evita duplicados y crea sale.order en Odoo.
    """
    try:
        result = process_external_order(db, payload)
    except OrderProcessingError as exc:
        raise HTTPException(status_code=422, detail=exc.message) from exc

    if result.duplicate:
        # 200 con flag duplicate=true también es válido; usamos 409 para dejarlo explícito
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Orden externa ya procesada",
                "order": result.model_dump(),
            },
        )
    return result


@router.get("/orders/stats/summary")
def get_orders_stats(db: Session = Depends(get_db)) -> dict:
    """Resumen de órdenes por estado (created / failed / ...)."""
    by_status = repo.count_orders_by_status(db)
    return {
        "by_status": by_status,
        "total": sum(by_status.values()),
    }


@router.get("/orders/{external_order_id}", response_model=OrderStatusOut)
def get_order_status(external_order_id: str, db: Session = Depends(get_db)) -> OrderStatusOut:
    order = repo.get_order_by_external_id(db, external_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden externa no encontrada")
    return OrderStatusOut(
        external_order_id=order.external_order_id,
        status=order.status,
        odoo_sale_order_id=order.odoo_sale_order_id,
        odoo_sale_order_name=order.odoo_sale_order_name,
        error_message=order.error_message,
        duplicate=False,
    )


@router.get("/orders/{external_order_id}/logs", response_model=list[IntegrationLogOut])
def get_order_logs(external_order_id: str, db: Session = Depends(get_db)) -> list[IntegrationLogOut]:
    order = repo.get_order_by_external_id(db, external_order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden externa no encontrada")
    logs = repo.list_logs(db, external_order_id)
    return [
        IntegrationLogOut(
            step=log.step,
            level=log.level,
            message=log.message,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
