from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ProcessedOrder(Base):
    __tablename__ = "processed_orders"
    __table_args__ = (UniqueConstraint("external_order_id", name="uq_external_order_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_order_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="received")
    odoo_sale_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odoo_sale_order_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    customer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class IntegrationLog(Base):
    __tablename__ = "integration_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_order_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    step: Mapped[str] = mapped_column(String(80), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
