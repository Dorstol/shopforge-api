from pydantic import AnyUrl, BaseModel


class PaymentUrlSchema(BaseModel):
    url: AnyUrl
