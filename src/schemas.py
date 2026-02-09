

from pydantic import BaseModel, HttpUrl, EmailStr, ConfigDict




class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

class UserReadSchema(BaseModel):
    id : int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)



class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"



class SubscriptionCreateSchema(BaseModel):
    url: HttpUrl
    target_price: float


class ProductReadSchema(BaseModel):
     url: str
     price: float | None

     model_config = ConfigDict(from_attributes=True)


class SubscriptionReadSchema(BaseModel):
    id: int
    target_price: float
    product: ProductReadSchema
    model_config = ConfigDict(from_attributes=True)

