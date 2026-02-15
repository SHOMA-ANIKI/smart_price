from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import User
from src.schemas import UserCreateSchema, TokenSchema
from src.auth import get_password_hash, verify_password, create_access_token, get_current_user
from src.utils.limiter import limiter  # Обновленный путь
from src.repositories.users import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.find_one_or_none(email=str(user_data.email))

    if user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = await repo.add({
        "email": str(user_data.email),
        "password": hashed_pwd
    })

    await db.commit()
    return {"message": "Успешная регистрация", "user_id": new_user.id}

@router.post("/login", response_model=TokenSchema)
@limiter.limit("10/minute")
async def login(request: Request, user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    user = await repo.find_one_or_none(email=user_data.username)

    if not user or not verify_password(user_data.password, str(user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная почта или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/me/telegram")
async def set_telegram_id(
    tg_chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = UserRepository(db)
    await repo.update_user(current_user.id, tg_chat_id=tg_chat_id)
    await db.commit()
    return {"message": "Telegram ID linked"}

