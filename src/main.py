from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from src.utils.limiter import limiter
from src.routers.auth import router as auth_router
from src.routers.products import router as products_router

app = FastAPI(title="SmartPrice API")

app.state.limiter = limiter # noqa
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(auth_router)
app.include_router(products_router)

@app.get("/")
async def root():
    return {"message": "SmartPrice API is running"}
