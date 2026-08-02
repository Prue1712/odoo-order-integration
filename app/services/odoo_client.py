"""Cliente mínimo de Odoo vía XML-RPC (estándar y fácil de explicar)."""

from __future__ import annotations

import xmlrpc.client
from typing import Any

from app.config import get_settings


class OdooClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.url = settings.odoo_url.rstrip("/")
        self.db = settings.odoo_db
        self.username = settings.odoo_user
        self.password = settings.odoo_password
        self.uid: int | None = None

        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise RuntimeError(
                f"Auth Odoo falló. db={self.db} user={self.username}. "
                "Verifica ODOO_PASSWORD en el archivo .env."
            )
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def _execute(self, model: str, method: str, args: list[Any], kwargs: dict[str, Any] | None = None) -> Any:
        # execute_kw(db, uid, password, model, method, args, kwargs)
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs or {},
        )

    def find_partner_by_email(self, email: str) -> dict[str, Any] | None:
        ids = self._execute(
            "res.partner",
            "search",
            [[("email", "=", email)]],
            {"limit": 1},
        )
        if not ids:
            return None
        partners = self._execute(
            "res.partner",
            "read",
            [ids],
            {"fields": ["id", "name", "email", "vat"]},
        )
        return partners[0] if partners else None

    def create_partner(self, name: str, email: str, vat: str | None = None) -> int:
        values: dict[str, Any] = {"name": name, "email": email, "customer_rank": 1}
        if vat:
            values["vat"] = vat
        return int(self._execute("res.partner", "create", [values]))

    def find_product_by_sku(self, sku: str) -> dict[str, Any] | None:
        # En Odoo, la "Referencia interna" es default_code
        ids = self._execute(
            "product.product",
            "search",
            [[("default_code", "=", sku)]],
            {"limit": 1},
        )
        if not ids:
            return None
        products = self._execute(
            "product.product",
            "read",
            [ids],
            {"fields": ["id", "name", "default_code", "list_price"]},
        )
        return products[0] if products else None

    def create_sale_order(
        self,
        partner_id: int,
        lines: list[dict[str, Any]],
        external_order_id: str,
    ) -> dict[str, Any]:
        """
        lines: [{product_id, quantity, price}, ...]
        client_order_ref guarda el ID externo (trazabilidad en Odoo).
        """
        order_lines = []
        for line in lines:
            order_lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": line["product_id"],
                        "product_uom_qty": line["quantity"],
                        "price_unit": line["price"],
                    },
                )
            )

        order_id = int(
            self._execute(
                "sale.order",
                "create",
                [
                    {
                        "partner_id": partner_id,
                        "client_order_ref": external_order_id,
                        "order_line": order_lines,
                    }
                ],
            )
        )
        data = self._execute(
            "sale.order",
            "read",
            [[order_id]],
            {"fields": ["id", "name", "client_order_ref", "state"]},
        )
        return data[0]
