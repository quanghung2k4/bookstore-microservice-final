"""
Neo4j Graph layer.
Schema:
  (:User {id, name})
  (:Product {id, name, category, price})
  (:Category {id, name})
  (:Query {id, text, user_id, timestamp})

Relationships:
  (User)-[:VIEWED {timestamp, duration}]->(Product)
  (User)-[:ADDED_TO_CART {timestamp}]->(Product)
  (User)-[:PURCHASED {timestamp, quantity}]->(Product)
  (User)-[:SEARCHED {timestamp}]->(Query)
  (Product)-[:BELONGS_TO]->(Category)
  (Query)-[:RELATED_TO]->(Product)
"""

from neo4j import GraphDatabase
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


_driver = None
_retry_after = 0
_RETRY_COOLDOWN_SECONDS = 5


def get_driver():
    global _driver, _retry_after
    if _driver is not None:
        return _driver

    now = time.monotonic()
    if now < _retry_after:
        return None

    try:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            connection_timeout=2,
            max_transaction_retry_time=2,
            connection_acquisition_timeout=2,
        )
        _driver.verify_connectivity()
        _retry_after = 0
    except Exception as e:
        logger.warning(f"Neo4j unavailable, will retry graph connection: {e}")
        if _driver is not None:
            try:
                _driver.close()
            except Exception:
                pass
        _driver = None
        _retry_after = now + _RETRY_COOLDOWN_SECONDS
    return _driver


def run_query(cypher, params=None):
    driver = get_driver()
    if driver is None:
        return []
    try:
        with driver.session() as session:
            result = session.run(cypher, params or {})
            return [dict(r) for r in result]
    except Exception as e:
        logger.warning(f"Neo4j query error: {e}")
        return []


# ── Node upserts ──────────────────────────────────────────────────────────────

def upsert_user(user_id, name=""):
    run_query(
        "MERGE (u:User {id: $id}) SET u.name = $name",
        {"id": str(user_id), "name": name},
    )


def upsert_product(product_id, name="", category="", price=0.0):
    run_query(
        "MERGE (p:Product {id: $id}) SET p.name=$name, p.category=$category, p.price=$price",
        {"id": str(product_id), "name": name, "category": category, "price": float(price)},
    )


def upsert_category(category_id, name=""):
    run_query(
        "MERGE (c:Category {id: $id}) SET c.name=$name",
        {"id": str(category_id), "name": name},
    )


def link_product_category(product_id, category_id):
    run_query(
        """
        MATCH (p:Product {id: $pid}), (c:Category {id: $cid})
        MERGE (p)-[:BELONGS_TO]->(c)
        """,
        {"pid": str(product_id), "cid": str(category_id)},
    )


# ── Behavior events ───────────────────────────────────────────────────────────

def record_view(user_id, product_id, duration=0, timestamp=None):
    if timestamp:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:VIEWED {timestamp: datetime($ts), duration: $dur}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id), "dur": duration, "ts": str(timestamp)}
    else:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:VIEWED {timestamp: datetime(), duration: $dur}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id), "dur": duration}

    run_query(cypher, params)


def record_cart_add(user_id, product_id, timestamp=None):
    if timestamp:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:ADDED_TO_CART {timestamp: datetime($ts)}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id), "ts": str(timestamp)}
    else:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:ADDED_TO_CART {timestamp: datetime()}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id)}

    run_query(cypher, params)


def record_purchase(user_id, product_id, quantity=1, timestamp=None):
    if timestamp:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:PURCHASED {timestamp: datetime($ts), quantity: $qty}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id), "qty": quantity, "ts": str(timestamp)}
    else:
        cypher = """
        MERGE (u:User {id: $uid})
        MERGE (p:Product {id: $pid})
        CREATE (u)-[:PURCHASED {timestamp: datetime(), quantity: $qty}]->(p)
        """
        params = {"uid": str(user_id), "pid": str(product_id), "qty": quantity}

    run_query(cypher, params)


def record_search(user_id, query_text, timestamp=None):
    if timestamp:
        cypher = """
        MERGE (u:User {id: $uid})
        CREATE (q:Query {id: randomUUID(), text: $text, timestamp: datetime($ts)})
        CREATE (u)-[:SEARCHED]->(q)
        """
        params = {"uid": str(user_id), "text": query_text, "ts": str(timestamp)}
    else:
        cypher = """
        MERGE (u:User {id: $uid})
        CREATE (q:Query {id: randomUUID(), text: $text, timestamp: datetime()})
        CREATE (u)-[:SEARCHED]->(q)
        """
        params = {"uid": str(user_id), "text": query_text}

    run_query(cypher, params)


# ── Recommendation queries ────────────────────────────────────────────────────

def get_collaborative_recommendations(user_id, limit=10):
    """Behavior-based collaborative filtering.

    Uses recent user interactions (VIEWED/ADDED_TO_CART/PURCHASED) as seeds,
    then recommends what similar users interacted with.
    """
    return run_query(
        """
        MATCH (u:User {id: $uid})
        MATCH (u)-[r:VIEWED|ADDED_TO_CART|PURCHASED]->(seed:Product)
                WITH u, seed, r,
                         CASE type(r)
                             WHEN 'PURCHASED' THEN 3
                             WHEN 'ADDED_TO_CART' THEN 2
                             ELSE 1
                         END AS seed_w
        ORDER BY r.timestamp DESC
        LIMIT 20
        MATCH (seed)<-[:VIEWED|ADDED_TO_CART|PURCHASED]-(other:User)
        WHERE other.id <> u.id
                MATCH (other)-[rr:VIEWED|ADDED_TO_CART|PURCHASED]->(rec:Product)
                WHERE rec.id <> seed.id
                    AND NOT (u)-[:VIEWED|ADDED_TO_CART|PURCHASED]->(rec)
                WITH rec, seed_w,
                         CASE type(rr)
                             WHEN 'PURCHASED' THEN 3
                             WHEN 'ADDED_TO_CART' THEN 2
                             ELSE 1
                         END AS rec_w
                RETURN rec.id AS product_id, rec.name AS name, sum(seed_w * rec_w) AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"uid": str(user_id), "limit": limit},
    )


def get_content_based_recommendations(user_id, limit=10):
    """Products in similar categories based on recent behavior."""

    primary = run_query(
        """
                MATCH (u:User {id: $uid})-[r:VIEWED|ADDED_TO_CART|PURCHASED]->(p:Product)-[:BELONGS_TO]->(c:Category)
                WITH u, c,
                         CASE type(r)
                             WHEN 'PURCHASED' THEN 3
                             WHEN 'ADDED_TO_CART' THEN 2
                             ELSE 1
                         END AS w
        MATCH (c)<-[:BELONGS_TO]-(rec:Product)
        WHERE NOT (u)-[:VIEWED|ADDED_TO_CART|PURCHASED]->(rec)
                RETURN rec.id AS product_id, rec.name AS name, sum(w) AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"uid": str(user_id), "limit": limit},
    )
    if primary:
        return primary

    # Fallback when Category nodes/relationships haven't been synced yet.
    return run_query(
        """
                MATCH (u:User {id: $uid})-[r:VIEWED|ADDED_TO_CART|PURCHASED]->(p:Product)
                WITH u,
                         p.category AS cat,
                         CASE type(r)
                             WHEN 'PURCHASED' THEN 3
                             WHEN 'ADDED_TO_CART' THEN 2
                             ELSE 1
                         END AS w
        WHERE cat IS NOT NULL AND trim(toString(cat)) <> ""
                WITH u, cat, sum(w) AS catScore
        MATCH (rec:Product)
                WHERE rec.category = cat
                    AND NOT (u)-[:VIEWED|ADDED_TO_CART|PURCHASED]->(rec)
                RETURN rec.id AS product_id, rec.name AS name, catScore AS score
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"uid": str(user_id), "limit": limit},
    )


def get_trending_products(limit=10):
    """Most purchased products in last 7 days."""
    return run_query(
        """
        MATCH (u:User)-[r:PURCHASED]->(p:Product)
        WHERE r.timestamp > datetime() - duration('P7D')
        RETURN p.id AS product_id, p.name AS name, count(r) AS score
        ORDER BY score DESC LIMIT $limit
        """,
        {"limit": limit},
    )


def get_user_behavior_sequence(user_id, limit=50):
    """Return ordered behavior sequence for LSTM input."""
    return run_query(
        """
        MATCH (u:User {id: $uid})-[r:VIEWED|ADDED_TO_CART|PURCHASED]->(p:Product)
        RETURN p.id AS product_id, type(r) AS action, r.timestamp AS ts
        ORDER BY ts ASC LIMIT $limit
        """,
        {"uid": str(user_id), "limit": limit},
    )


def search_products_by_query(query_text, limit=10):
    """Full-text style search via graph — find products related to similar queries."""
    return run_query(
        """
        MATCH (q:Query)-[:RELATED_TO]->(p:Product)
        WHERE toLower(q.text) CONTAINS toLower($text)
        RETURN DISTINCT p.id AS product_id, p.name AS name, count(*) AS score
        ORDER BY score DESC LIMIT $limit
        """,
        {"text": query_text, "limit": limit},
    )
