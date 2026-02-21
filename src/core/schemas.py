from pydantic import BaseModel, HttpUrl, EmailStr, ConfigDict
from typing import Optional

class BaseReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

class UserReadSchema(BaseReadSchema):
    id: int
    email: EmailStr
    tg_chat_id: Optional[int] = None

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SubscriptionCreateSchema(BaseModel):
    url: HttpUrl
    target_price: float

class ProductReadSchema(BaseReadSchema):
    id: int
    url: str
    price: Optional[float] = None

class SubscriptionReadSchema(BaseReadSchema):
    id: int
    target_price: float
    product: ProductReadSchema

class UserStatsSchema(BaseReadSchema):
    total_subscriptions: int
    active_monitors: int
