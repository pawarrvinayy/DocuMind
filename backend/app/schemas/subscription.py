from pydantic import BaseModel


class CheckoutSessionOut(BaseModel):
    checkout_url: str


class SubscriptionOut(BaseModel):
    plan: str
    status: str

    model_config = {"from_attributes": True}


class UsageBucket(BaseModel):
    used: int
    limit: int | None  # None = unlimited (Pro plan)


class UsageOut(BaseModel):
    plan: str
    period: str          # "YYYY-MM"
    documents: UsageBucket
    queries: UsageBucket
