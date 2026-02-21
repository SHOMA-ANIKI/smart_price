from fastapi import APIRouter, Depends, status
from src.use_case import ProductService
from src.api.dependencies import get_current_user_id, get_product_service
from src.core.schemas import SubscriptionCreateSchema
router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe(
    sub_data: SubscriptionCreateSchema,
    current_user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
):
    return await service.subscribe_to_product(current_user_id, sub_data)

@router.get("/top-drops")
async def get_top_drops(
    limit: int = 10,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_top_price_drops(limit)

@router.post("/refresh-my-prices")
async def refresh_my_prices(
    current_user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
):
    return await service.trigger_price_update(current_user_id)

@router.get("/stats")
async def get_my_stats(
    current_user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
):
    return await service.get_user_stats(current_user_id)

@router.delete("/clear-all")
async def clear_all_subscriptions(
    current_user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
):
    return await service.clear_user_subscriptions(current_user_id)

@router.get("/{product_id}")
async def get_details(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_product_details(product_id)

@router.delete("/unsubscribe/{product_id}")
async def unsubscribe(
    product_id: int,
    current_user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_product_service)
):
    return await service.remove_subscription(current_user_id, product_id)
