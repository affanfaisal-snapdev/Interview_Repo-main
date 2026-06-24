"""
Tests for ecommerce product and order endpoints.
"""

from fastapi import status

from app.db.ecommerce import seed_ecommerce_data


def test_list_products_returns_seeded_catalog(client, db):
    """Products endpoint should expose a seeded catalog with dozens of entries."""
    seed_ecommerce_data(db)

    response = client.get("/api/v1/products")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 24
    assert data[0]["name"]
    assert data[0]["category"]
    assert isinstance(data[0]["price"], float)


def test_list_orders_returns_seeded_orders_with_product_details(client, db):
    """Orders endpoint should expose seeded orders joined with product data."""
    seed_ecommerce_data(db)

    response = client.get("/api/v1/orders")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 36
    assert data[0]["product_id"]
    assert data[0]["product_name"]
    assert data[0]["customer_email"].endswith("@example.com")
    assert data[0]["status"] in {
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    }
