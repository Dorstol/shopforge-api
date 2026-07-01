from pydantic import AnyUrl, BaseModel


class PaymentUrlSchema(BaseModel):
    url: AnyUrl


class SetOrderToClosedSchema(BaseModel):
    is_closed: bool = True
