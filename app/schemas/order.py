from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerIn(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    vat: str | None = None
    # Campos opcionales → se mapean a res.partner en Odoo
    phone: str | None = None
    mobile: str | None = None
    website: str | None = None
    job_position: str | None = None  # Odoo: function (Puesto de trabajo)
    is_company: bool = False  # True = Empresa, False = Persona


class OrderLineIn(BaseModel):
    sku: str = Field(min_length=1)
    quantity: float
    price: float

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("quantity must be > 0")
        return value

    @field_validator("price")
    @classmethod
    def price_must_be_valid(cls, value: float) -> float:
        if value < 0:
            raise ValueError("price must be >= 0")
        return value


class ExternalOrderIn(BaseModel):
    external_order_id: str = Field(min_length=1)
    customer: CustomerIn
    lines: list[OrderLineIn] = Field(min_length=1)


class OrderStatusOut(BaseModel):
    external_order_id: str
    status: str
    odoo_sale_order_id: int | None = None
    odoo_sale_order_name: str | None = None
    error_message: str | None = None
    duplicate: bool = False


class IntegrationLogOut(BaseModel):
    step: str
    level: str
    message: str
    created_at: str
