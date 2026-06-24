"""
API routers for ecommerce-style product and order endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.base import get_db
from app.db.ecommerce import OrderRepository, ProductRepository
from app.schemas.ecommerce import OrderResponse, ProductResponse

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/products",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List all products",
)
async def list_products(
    db: Session = Depends(get_db),
) -> list[ProductResponse]:
    """
    Return all seeded products in the catalog.
    """
    try:
        products = ProductRepository(db).list_products()
        return [ProductResponse.model_validate(product) for product in products]
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products",
        )


@router.get(
    "/orders",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="List all orders",
)
async def list_orders(
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    """
    Return all seeded ecommerce orders.
    """
    try:
        orders = OrderRepository(db).list_orders()
        return [
            OrderResponse(
                id=order.id,
                product_id=order.product_id,
                product_name=order.product.name,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                shipping_address=order.shipping_address,
                quantity=order.quantity,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at,
                updated_at=order.updated_at,
            )
            for order in orders
        ]
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders",
        )
