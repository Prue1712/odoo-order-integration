from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes_orders import router as orders_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Odoo Order Integration API",
    description="Recibe pedidos externos, valida y crea órdenes de venta en Odoo 18.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(orders_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/debug/odoo-config")
def debug_odoo_config() -> dict[str, str]:
    """Muestra qué credenciales está usando la API (sin password)."""
    from app.config import get_settings

    s = get_settings()
    return {
        "odoo_url": s.odoo_url,
        "odoo_db": s.odoo_db,
        "odoo_user": s.odoo_user,
        "password_set": "yes" if s.odoo_password else "no",
        "env_file": str((__import__("app.config", fromlist=["ENV_FILE"]).ENV_FILE)),
    }
