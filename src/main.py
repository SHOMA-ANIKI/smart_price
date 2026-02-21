from fastapi import FastAPI
from src.core.config import settings

from src.api.routers.auth import router as auth_router
from src.api.routers.products import router as products_router

app = FastAPI(
    title="SmartPrice API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

app.include_router(
    products_router,
    prefix=f"{settings.API_V1_STR}/products",
    tags=["Products & Subscriptions"]
)

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "version": "1.0.0",
        "api_prefix": settings.API_V1_STR
    }
