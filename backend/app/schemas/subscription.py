from pydantic import BaseModel


class CheckoutSessionOut(BaseModel):
    checkout_url: str


class SubscriptionOut(BaseModel):
    plan: str
    status: str

    model_config = {"from_attributes": True}
