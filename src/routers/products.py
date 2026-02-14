import redis
from fastapi import APIRouter, Depends, HTTPException, status
from src.models import User
from src.schemas import SubscriptionCreateSchema, SubscriptionReadSchema
from src.auth import get_current_user
from src.worker import fetch_product_price
from src.config import settings
from src.utils.unit_of_work import UnitOfWork

router = APIRouter(prefix="/products", tags=["Products"])
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.post("/subscribe")
async def subscribe_to_product(
        sub_data: SubscriptionCreateSchema,
        current_user: User = Depends(get_current_user)
):
    async with UnitOfWork() as uow:
        product = await uow.products.find_one_or_none(url=str(sub_data.url))

        if not product:
            product = await uow.products.add({"url": str(sub_data.url)})
            await uow.session.flush()

        try:
            await uow.subs.add({
                "user_id": current_user.id,
                "product_id": product.id,
                "target_price": sub_data.target_price
            })
            fetch_product_price.delay(product.id)
        except Exception:
            raise HTTPException(status_code=400, detail="Вы уже подписаны на этот товар")

    return {"message": "Подписка оформлена", "product_id": product.id}


@router.delete("/unsubscribe/{product_id}")
async def unsubscribe(
        product_id: int,
        current_user: User = Depends(get_current_user)
):
    async with UnitOfWork() as uow:
        sub = await uow.subs.find_one_or_none(user_id=current_user.id, product_id=product_id)
        if not sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена")

        await uow.subs.delete_sub(user_id=current_user.id, product_id=product_id)

    return {"message": "Вы успешно отписались от обновлений товара"}


@router.patch("/subscriptions/{sub_id}")
async def update_subscription_price(
        sub_id: int,
        new_target_price: float,
        current_user: User = Depends(get_current_user)
):
    async with UnitOfWork() as uow:
        updated_sub = await uow.subs.update_target_price(
            sub_id=sub_id,
            user_id=current_user.id,
            new_price=new_target_price
        )
        if not updated_sub:
            raise HTTPException(status_code=404, detail="Подписка не найдена или доступ запрещен")

    return {"message": "Целевая цена успешно обновлена", "new_target_price": updated_sub.target_price}


@router.get("/{product_id}")
async def get_product_details(product_id: int):
    async with UnitOfWork() as uow:
        product = await uow.products.find_one_or_none(id=product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        cached_price = redis_client.get(f"product_price:{product.id}")
        if cached_price:
            product.price = float(cached_price)

        return product
