"""
Repository and seed helpers for ecommerce-style data.
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.core.logging import get_logger
from app.db.models import OrderModel, ProductModel

logger = get_logger(__name__)


PRODUCT_SEED_DATA = [
    {
        "name": "Aurora Wireless Headphones",
        "category": "Electronics",
        "description": "Noise-cancelling over-ear headphones with 40-hour battery life.",
        "price": 129.99,
        "stock_quantity": 34,
        "image_url": "https://example.com/products/aurora-headphones.jpg",
    },
    {
        "name": "Nimbus Mechanical Keyboard",
        "category": "Electronics",
        "description": "Compact hot-swappable keyboard with tactile switches.",
        "price": 89.50,
        "stock_quantity": 21,
        "image_url": "https://example.com/products/nimbus-keyboard.jpg",
    },
    {
        "name": "Summit Running Shoes",
        "category": "Footwear",
        "description": "Lightweight road-running shoes with breathable mesh upper.",
        "price": 74.95,
        "stock_quantity": 46,
        "image_url": "https://example.com/products/summit-shoes.jpg",
    },
    {
        "name": "Harbor Canvas Backpack",
        "category": "Accessories",
        "description": "Durable commuter backpack with padded laptop sleeve.",
        "price": 59.99,
        "stock_quantity": 28,
        "image_url": "https://example.com/products/harbor-backpack.jpg",
    },
    {
        "name": "Luna Smart Watch",
        "category": "Wearables",
        "description": "Fitness-focused smartwatch with sleep and heart-rate tracking.",
        "price": 149.00,
        "stock_quantity": 19,
        "image_url": "https://example.com/products/luna-watch.jpg",
    },
    {
        "name": "Cedar Ceramic Mug Set",
        "category": "Home",
        "description": "Set of four matte ceramic mugs for coffee and tea lovers.",
        "price": 32.75,
        "stock_quantity": 55,
        "image_url": "https://example.com/products/cedar-mugs.jpg",
    },
    {
        "name": "Solstice Linen Shirt",
        "category": "Apparel",
        "description": "Relaxed-fit linen shirt designed for warm-weather comfort.",
        "price": 44.20,
        "stock_quantity": 37,
        "image_url": "https://example.com/products/solstice-shirt.jpg",
    },
    {
        "name": "Atlas Protein Blender",
        "category": "Kitchen",
        "description": "Portable blender with USB-C charging for shakes on the go.",
        "price": 39.90,
        "stock_quantity": 26,
        "image_url": "https://example.com/products/atlas-blender.jpg",
    },
    {
        "name": "Breeze Table Lamp",
        "category": "Home",
        "description": "Minimal bedside lamp with adjustable warm light levels.",
        "price": 27.40,
        "stock_quantity": 31,
        "image_url": "https://example.com/products/breeze-lamp.jpg",
    },
    {
        "name": "Trail Stainless Bottle",
        "category": "Outdoors",
        "description": "Insulated bottle that keeps drinks cold for 24 hours.",
        "price": 24.99,
        "stock_quantity": 63,
        "image_url": "https://example.com/products/trail-bottle.jpg",
    },
    {
        "name": "Nova Yoga Mat",
        "category": "Fitness",
        "description": "Non-slip yoga mat with alignment guides and carry strap.",
        "price": 36.80,
        "stock_quantity": 42,
        "image_url": "https://example.com/products/nova-yoga-mat.jpg",
    },
    {
        "name": "Maple Bed Sheet Set",
        "category": "Home",
        "description": "Soft microfiber queen sheet set with deep-pocket fit.",
        "price": 48.60,
        "stock_quantity": 24,
        "image_url": "https://example.com/products/maple-sheets.jpg",
    },
    {
        "name": "Orbit Gaming Mouse",
        "category": "Electronics",
        "description": "High-precision gaming mouse with programmable buttons.",
        "price": 52.30,
        "stock_quantity": 29,
        "image_url": "https://example.com/products/orbit-mouse.jpg",
    },
    {
        "name": "Willow Denim Jacket",
        "category": "Apparel",
        "description": "Classic denim jacket with relaxed everyday styling.",
        "price": 67.45,
        "stock_quantity": 18,
        "image_url": "https://example.com/products/willow-jacket.jpg",
    },
    {
        "name": "Echo Bluetooth Speaker",
        "category": "Electronics",
        "description": "Portable speaker with deep bass and IPX7 water resistance.",
        "price": 58.99,
        "stock_quantity": 33,
        "image_url": "https://example.com/products/echo-speaker.jpg",
    },
    {
        "name": "Pine Desk Organizer",
        "category": "Office",
        "description": "Wooden desktop organizer for notebooks, pens, and tech accessories.",
        "price": 21.15,
        "stock_quantity": 47,
        "image_url": "https://example.com/products/pine-organizer.jpg",
    },
    {
        "name": "Terra Gardening Kit",
        "category": "Garden",
        "description": "Starter herb gardening kit with tools, pots, and seeds.",
        "price": 41.25,
        "stock_quantity": 22,
        "image_url": "https://example.com/products/terra-garden-kit.jpg",
    },
    {
        "name": "Comet Kids Sneakers",
        "category": "Footwear",
        "description": "Easy-slip sneakers for kids with durable rubber sole.",
        "price": 34.70,
        "stock_quantity": 40,
        "image_url": "https://example.com/products/comet-kids-sneakers.jpg",
    },
    {
        "name": "Drift Car Phone Mount",
        "category": "Automotive",
        "description": "Dashboard phone mount with one-touch lock mechanism.",
        "price": 18.99,
        "stock_quantity": 58,
        "image_url": "https://example.com/products/drift-mount.jpg",
    },
    {
        "name": "Sierra Travel Pillow",
        "category": "Travel",
        "description": "Memory-foam neck pillow with washable cover.",
        "price": 26.50,
        "stock_quantity": 36,
        "image_url": "https://example.com/products/sierra-pillow.jpg",
    },
    {
        "name": "Glow Skincare Bundle",
        "category": "Beauty",
        "description": "Three-step skincare set with cleanser, serum, and moisturizer.",
        "price": 64.90,
        "stock_quantity": 17,
        "image_url": "https://example.com/products/glow-bundle.jpg",
    },
    {
        "name": "Forge Cast Iron Pan",
        "category": "Kitchen",
        "description": "Pre-seasoned cast iron pan for stovetop and oven cooking.",
        "price": 54.10,
        "stock_quantity": 27,
        "image_url": "https://example.com/products/forge-pan.jpg",
    },
    {
        "name": "Ripple Bath Towel Set",
        "category": "Home",
        "description": "Quick-dry cotton towel set with plush texture.",
        "price": 38.25,
        "stock_quantity": 44,
        "image_url": "https://example.com/products/ripple-towels.jpg",
    },
    {
        "name": "Vertex Laptop Stand",
        "category": "Office",
        "description": "Aluminum stand to improve desk ergonomics and airflow.",
        "price": 29.80,
        "stock_quantity": 39,
        "image_url": "https://example.com/products/vertex-stand.jpg",
    },
]

CUSTOMER_NAMES = [
    "Ava Thompson",
    "Noah Martinez",
    "Sophia Patel",
    "Liam Johnson",
    "Emma Walker",
    "James Kim",
    "Olivia Rivera",
    "Benjamin Scott",
    "Mia Turner",
    "Lucas Evans",
    "Charlotte Reed",
    "Henry Brooks",
]

ORDER_STATUSES = [
    "pending",
    "processing",
    "shipped",
    "delivered",
    "cancelled",
]


class ProductRepository:
    """
    Repository for product catalog operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_products(self) -> list[ProductModel]:
        return (
            self.db.query(ProductModel)
            .order_by(ProductModel.created_at.desc(), ProductModel.name.asc())
            .all()
        )


class OrderRepository:
    """
    Repository for order operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def list_orders(self) -> list[OrderModel]:
        return (
            self.db.query(OrderModel)
            .options(joinedload(OrderModel.product))
            .order_by(OrderModel.created_at.desc())
            .all()
        )


def seed_ecommerce_data(db: Session) -> None:
    """
    Seed products and orders once when the database is empty.
    """
    product_count = db.query(ProductModel).count()
    order_count = db.query(OrderModel).count()

    if product_count > 0 and order_count > 0:
        logger.info("Ecommerce seed skipped because products and orders already exist")
        return

    products = []
    if product_count == 0:
        for product_data in PRODUCT_SEED_DATA:
            product = ProductModel(**product_data)
            db.add(product)
            products.append(product)
        db.flush()
        logger.info("Seeded %s products", len(products))
    else:
        products = (
            db.query(ProductModel)
            .order_by(ProductModel.created_at.asc(), ProductModel.name.asc())
            .all()
        )

    if order_count == 0:
        base_time = datetime.utcnow() - timedelta(days=30)
        for index in range(36):
            product = products[index % len(products)]
            customer_name = CUSTOMER_NAMES[index % len(CUSTOMER_NAMES)]
            quantity = (index % 4) + 1
            order = OrderModel(
                product_id=product.id,
                customer_name=customer_name,
                customer_email=customer_name.lower().replace(" ", ".") + "@example.com",
                shipping_address=f"{100 + index} Market Street, Suite {10 + (index % 8)}, Demo City",
                quantity=quantity,
                status=ORDER_STATUSES[index % len(ORDER_STATUSES)],
                total_amount=round(product.price * quantity, 2),
                created_at=base_time + timedelta(hours=index * 9),
                updated_at=base_time + timedelta(hours=index * 9, minutes=45),
            )
            db.add(order)
        logger.info("Seeded 36 orders")

    db.commit()
