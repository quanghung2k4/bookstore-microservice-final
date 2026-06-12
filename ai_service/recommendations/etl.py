"""
ETL Pipeline — syncs data from product/order services into Neo4j graph.
Can be run as a management command or triggered via API.
"""

import logging
import requests
from django.conf import settings
from . import graph

logger = logging.getLogger(__name__)


def _get(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.warning(f"ETL fetch failed {url}: {e}")
        return None


def sync_products():
    """Pull all products from product_service and upsert into Neo4j."""
    count = 0
    url = f"{settings.PRODUCT_SERVICE_URL}/api/products/?page_size=200"
    while url:
        data = _get(url)
        if not data:
            break
        items = data if isinstance(data, list) else data.get("results", [])
        next_url = data.get("next") if isinstance(data, dict) else None

        for p in items:
            cat = p.get("category") or {}
            cat_id = cat.get("id", "") if isinstance(cat, dict) else str(cat)
            cat_name = cat.get("name", "") if isinstance(cat, dict) else ""

            graph.upsert_product(
                product_id=p["id"],
                name=p.get("name", ""),
                category=cat_name,
                price=float(p.get("price", 0)),
            )
            if cat_id:
                graph.upsert_category(cat_id, cat_name)
                graph.link_product_category(p["id"], cat_id)
            count += 1

        url = next_url

    logger.info(f"ETL: synced {count} products to Neo4j")
    return count


def sync_orders():
    """Pull orders and record PURCHASED events in Neo4j."""
    data = _get(f"{settings.ORDER_SERVICE_URL}/api/orders/")
    if not data:
        return 0

    items = data if isinstance(data, list) else data.get("results", [])
    count = 0
    for order in items:
        user_id = order.get("user_id")
        if not user_id:
            continue
        graph.upsert_user(user_id)
        for item in order.get("items", []):
            graph.record_purchase(
                user_id=user_id,
                product_id=item.get("product_id"),
                quantity=item.get("quantity", 1),
            )
            count += 1

    logger.info(f"ETL: synced {count} purchase events to Neo4j")
    return count


def run_full_etl():
    products = sync_products()
    purchases = sync_orders()
    return {"products_synced": products, "purchases_synced": purchases}
