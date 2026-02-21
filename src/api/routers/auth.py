from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from src.api.dependencies import get_auth_service, get_current_user_id
from src.core.schemas import UserCreateSchema, TokenSchema

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateSchema,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(user_data)

@router.post("/login", response_model=TokenSchema)
async def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    return await service.authenticate_user(user_data.username, user_data.password)

@router.patch("/me/telegram")
async def set_telegram_id(
    tg_chat_id: int,
    service: AuthService = Depends(get_auth_service),
    current_user_id: int = Depends(get_current_user_id)
):
    return await service.link_telegram(current_user_id, tg_chat_id)
