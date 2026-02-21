from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from src.api.dependencies import get_auth_service, get_current_user_id
from src.use_cases.auth_service import AuthService
from src.core.schemas import UserCreateSchema, TokenSchema

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateSchema,
    service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя через Use Case слой."""
    return await service.register_user(user_data)

@router.post("/login", response_model=TokenSchema)
async def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """Аутентификация и выдача JWT токена."""
    return await service.authenticate_user(user_data.username, user_data.password)

@router.patch("/me/telegram")
async def set_telegram_id(
    tg_chat_id: int,
    service: AuthService = Depends(get_auth_service),
    current_user_id: int = Depends(get_current_user_id) # Зависимость для парсинга JWT
):
    """Привязка Telegram ID к текущему пользователю."""
    return await service.link_telegram(current_user_id, tg_chat_id)
