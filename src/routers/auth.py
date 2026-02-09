from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models import User
from src.schemas import UserCreateSchema, TokenSchema
from src.auth import get_password_hash, verify_password, create_access_token
from src.utils import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(email=str(user_data.email), password=hashed_pwd)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Успешная регистрация", "user_id": new_user.id}

@router.post("/login", response_model=TokenSchema)
@limiter.limit("10/minute")
async def login(request: Request, user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, str(user.password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная почта или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
