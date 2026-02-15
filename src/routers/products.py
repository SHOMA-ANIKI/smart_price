import redis
from fastapi import APIRouter, Depends, HTTPException, status
from src.auth import get_current_user
from src.models import User
from src.schemas import SubscriptionCreateSchema, SubscriptionReadSchema
from src.utils.unit_of_work import UnitOfWork
from src.worker import fetch_product_price
from src.config import settings

router = APIRouter(prefix="/products", tags=["Products"])
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@router.post("/subscribe")
async def subscribe(sub_data: SubscriptionCreateSchema, current_user: User = Depends(get_current_user)):
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
            raise HTTPException(status_code=400, detail="Already subscribed")
    return {"message": "Subscribed", "product_id": product.id}

@router.get("/top-drops")
async def get_top_drops(limit: int = 10):
    async with UnitOfWork() as uow:
        return await uow.products.get_top_drops(limit)

@router.post("/refresh-my-prices")
async def refresh_my_prices(current_user: User = Depends(get_current_user)):
    async with UnitOfWork() as uow:
        subs = await uow.subs.get_user_subs(current_user.id)
        for sub in subs:
            fetch_product_price.delay(sub.product_id)
    return {"message": f"Update triggered for {len(subs)} items"}

@router.get("/stats")
async def get_my_stats(current_user: User = Depends(get_current_user)):
    async with UnitOfWork() as uow:
        return await uow.subs.get_user_stats(current_user.id)

@router.delete("/clear-all")
async def clear_all_subscriptions(current_user: User = Depends(get_current_user)):
    async with UnitOfWork() as uow:
        await uow.subs.delete_all_user_subs(current_user.id)
    return {"message": "All subscriptions deleted"}

@router.get("/{product_id}")
async def get_details(product_id: int):
    async with UnitOfWork() as uow:
        product = await uow.products.find_one_or_none(id=product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Not found")
        cached_price = redis_client.get(f"product_price:{product.id}")
        if cached_price:
            product.price = float(cached_price)
        return product

@router.delete("/unsubscribe/{product_id}")
async def unsubscribe(product_id: int, current_user: User = Depends(get_current_user)):
    async with UnitOfWork() as uow:
        await uow.subs.delete_sub(user_id=current_user.id, product_id=product_id)
    return {"message": "Unsubscribed"}
