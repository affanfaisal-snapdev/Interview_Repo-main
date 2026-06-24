"""
Read-only NL-to-SQL service for ecommerce chat queries.
"""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.services.gemini_client import GeminiClient, Message

logger = get_logger(__name__)


class NLToSQLService:
    """
    Translate natural language into safe, read-only SQL over ecommerce tables.
    """

    ALLOWED_TABLES = {"products", "orders"}
    FORBIDDEN_SQL_TOKENS = {
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "replace",
        "attach",
        "detach",
        "pragma",
    }

    SCHEMA_DESCRIPTION = """
You can query only these SQLite tables:

Table: products
- id TEXT primary key
- name TEXT
- category TEXT
- description TEXT
- price REAL
- stock_quantity INTEGER
- image_url TEXT
- is_active BOOLEAN
- created_at DATETIME

Table: orders
- id TEXT primary key
- product_id TEXT foreign key to products.id
- customer_name TEXT
- customer_email TEXT
- shipping_address TEXT
- quantity INTEGER
- status TEXT
- total_amount REAL
- created_at DATETIME
- updated_at DATETIME

Join rule:
- orders.product_id = products.id
""".strip()

    def __init__(self, db: Session, gemini_client: GeminiClient | None = None):
        self.db = db
        self.gemini_client = gemini_client or GeminiClient()

    @staticmethod
    def is_ecommerce_query(user_message: str) -> bool:
        """
        Lightweight intent check for products/orders database questions.
        """
        normalized = user_message.lower()
        keywords = (
            "product",
            "products",
            "order",
            "orders",
            "price",
            "stock",
            "category",
            "customer",
            "status",
            "quantity",
            "total amount",
            "sold",
            "inventory",
        )
        return any(keyword in normalized for keyword in keywords)

    async def try_handle_query(self, user_message: str) -> str | None:
        """
        Return a database-backed answer when the request fits products/orders data.
        Return None when the message should fall back to the normal chat flow.
        """
        sql = await self.generate_sql(user_message)
        if sql == "UNSUPPORTED":
            return None

        validated_sql = self.validate_sql(sql)
        rows = self.execute_sql(validated_sql)
        return self.format_response(rows)

    async def generate_sql(self, user_message: str) -> str:
        prompt = (
            "Convert the user's request into a single SQLite SELECT query.\n"
            "If the request cannot be answered using only the products and orders tables, "
            "respond with exactly UNSUPPORTED.\n"
            "Never write anything except SQL or UNSUPPORTED.\n"
            "Never use markdown fences.\n"
            "Only generate read-only SELECT statements.\n"
            "Use table names exactly as provided.\n\n"
            f"{self.SCHEMA_DESCRIPTION}\n\n"
            f"User request: {user_message}"
        )

        response = await self.gemini_client.generate_response(
            messages=[Message(role="user", content=prompt)],
            temperature=0.1,
            max_output_tokens=512,
            system_instruction=(
                "You are a SQL translator. Produce only safe SQLite SELECT queries "
                "for the products and orders tables."
            ),
        )

        cleaned_response = self._strip_code_fences(response).strip()
        logger.info("Generated SQL candidate for ecommerce chat query")
        return cleaned_response

    async def repair_sql(
        self,
        user_message: str,
        failed_sql: str,
        error_message: str,
    ) -> str:
        prompt = (
            "The previous SQLite query for the user's ecommerce request failed.\n"
            "Return a corrected single SQLite SELECT query, or UNSUPPORTED if it cannot "
            "be answered from products and orders.\n"
            "Never use markdown fences.\n"
            "Never return anything except SQL or UNSUPPORTED.\n\n"
            f"{self.SCHEMA_DESCRIPTION}\n\n"
            f"User request: {user_message}\n"
            f"Previous SQL: {failed_sql}\n"
            f"Error: {error_message}"
        )

        response = await self.gemini_client.generate_response(
            messages=[Message(role="user", content=prompt)],
            temperature=0.1,
            max_output_tokens=512,
            system_instruction=(
                "You repair SQLite SELECT queries for products and orders only."
            ),
        )
        return self._strip_code_fences(response).strip()

    @staticmethod
    def _strip_code_fences(value: str) -> str:
        cleaned = value.strip()
        cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()

    def validate_sql(self, sql: str) -> str:
        normalized = " ".join(sql.strip().split())
        lowered = normalized.lower()

        if "--" in lowered or "/*" in lowered or "*/" in lowered:
            raise ValueError("Only plain read-only SQL queries are supported.")

        if ";" in lowered:
            raise ValueError("Only a single SQL statement is supported.")

        if not lowered.startswith("select "):
            raise ValueError("Only SELECT queries are supported.")

        for token in self.FORBIDDEN_SQL_TOKENS:
            if re.search(rf"\b{token}\b", lowered):
                raise ValueError("Only read-only queries against products and orders are supported.")

        referenced_tables = {
            match.group(1)
            for match in re.finditer(r"\b(?:from|join)\s+([a-z_][a-z0-9_]*)\b", lowered)
        }
        if not referenced_tables:
            raise ValueError("The query must reference products or orders.")

        if not referenced_tables.issubset(self.ALLOWED_TABLES):
            raise ValueError("Queries may only access the products and orders tables.")

        if " limit " not in f" {lowered} ":
            normalized = f"{normalized} LIMIT 50"

        return normalized

    def execute_sql(self, sql: str) -> list[dict[str, Any]]:
        try:
            result = self.db.execute(text(sql))
            return [dict(row) for row in result.mappings().all()]
        except SQLAlchemyError as exc:
            logger.error("Failed to execute ecommerce SQL query: %s", exc, exc_info=True)
            raise ValueError("I could not run that products/orders query safely.") from exc

    def format_response(self, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "I couldn't find any matching records in the products/orders data."

        lines = [f"I found {len(rows)} matching record(s):"]
        for row in rows[:10]:
            lines.append(f"- {self._format_row(row)}")

        if len(rows) > 10:
            lines.append(f"...and {len(rows) - 10} more.")

        return "\n".join(lines)

    @staticmethod
    def _format_row(row: dict[str, Any]) -> str:
        preferred_order = [
            "name",
            "category",
            "price",
            "stock_quantity",
            "status",
            "quantity",
            "total_amount",
            "customer_name",
            "customer_email",
            "description",
            "created_at",
            "updated_at",
            "id",
            "product_id",
            "image_url",
            "shipping_address",
            "is_active",
        ]

        label_map = {
            "name": "Product",
            "category": "Category",
            "price": "Price",
            "stock_quantity": "Stock",
            "status": "Status",
            "quantity": "Quantity",
            "total_amount": "Total",
            "customer_name": "Customer",
            "customer_email": "Email",
            "description": "Description",
            "created_at": "Created",
            "updated_at": "Updated",
            "id": "ID",
            "product_id": "Product ID",
            "image_url": "Image",
            "shipping_address": "Shipping address",
            "is_active": "Active",
        }

        ordered_keys = [key for key in preferred_order if key in row]
        ordered_keys.extend(key for key in row if key not in ordered_keys)

        parts = []
        for key in ordered_keys:
            value = row[key]
            if isinstance(value, float) and key in {"price", "total_amount"}:
                display_value = f"${value:,.2f}"
            elif isinstance(value, bool):
                display_value = "Yes" if value else "No"
            else:
                display_value = str(value)

            parts.append(f"{label_map.get(key, key.replace('_', ' ').title())}: {display_value}")

        return "; ".join(parts)
