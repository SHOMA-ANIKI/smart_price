
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from src.core.config import settings
from src.use_cases.auth_service import AuthService
from src.infrastructure.unit_of_work import UnitOfWork, IUnitOfWork
from src.use_case.subscriptions import SubscribeUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_uow():
    return UnitOfWork()

def get_auth_service(uow: IUnitOfWork = Depends(get_uow)):
    return AuthService(uow)

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    uow: IUnitOfWork = Depends(get_uow)
):
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

async def get_uow():
    return UnitOfWork()


def get_product_service(uow: UnitOfWork = Depends(get_uow)):
    return SubscribeUseCase(uow)
