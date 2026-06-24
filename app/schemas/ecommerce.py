"""
Pydantic schemas for ecommerce product and order endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ProductResponse(BaseModel):
    """Serialized product details."""

    id: str = Field(..., description="Product identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    description: str = Field(..., description="Product description")
    price: float = Field(..., description="Current product price")
    stock_quantity: int = Field(..., description="Available stock count")
    image_url: str | None = Field(None, description="Product image URL")
    is_active: bool = Field(..., description="Whether the product is active")
    created_at: datetime = Field(..., description="Product creation timestamp")

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Serialized order details."""

    id: str = Field(..., description="Order identifier")
    product_id: str = Field(..., description="Ordered product identifier")
    product_name: str = Field(..., description="Ordered product name")
    customer_name: str = Field(..., description="Customer full name")
    customer_email: EmailStr = Field(..., description="Customer email address")
    shipping_address: str = Field(..., description="Shipping address")
    quantity: int = Field(..., description="Quantity ordered")
    status: str = Field(..., description="Order status")
    total_amount: float = Field(..., description="Total order amount")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime | None = Field(..., description="Order update timestamp")
