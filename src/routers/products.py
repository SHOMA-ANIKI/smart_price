import redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.models import User, Product, Subscription
from src.schemas import SubscriptionCreateSchema, SubscriptionReadSchema
from src.auth import get_current_user
from src.worker import fetch_product_price
from src.config import settings

router = APIRouter(prefix="/products", tags=["Products"])


redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.post("/subscribe")
async def subscribe_to_product(
    sub_data: SubscriptionCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    product_stmt = select(Product).where(Product.url == str(sub_data.url))
    result = await db.execute(product_stmt)
    product = result.scalar_one_or_none()

    if not product:
        product = Product(url=str(sub_data.url))
        db.add(product)
        await db.flush()


    new_sub = Subscription(
        user_id=current_user.id,
        product_id=product.id,
        target_price=sub_data.target_price
    )

    try:
        db.add(new_sub)
        await db.commit()
        fetch_product_price.delay(product.id)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Вы уже подписаны на этот товар")

    return {"message": "Подписка оформлена", "product_id": product.id}


@router.get("/my", response_model=list[SubscriptionReadSchema])
async def get_my_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Subscription)
        .options(selectinload(Subscription.product))
        .where(Subscription.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    subscriptions = result.scalars().all()


    for sub in subscriptions:
        cached_price = redis_client.get(f"product_price:{sub.product_id}")
        if cached_price:
            sub.product.price = float(cached_price)

    return subscriptions
