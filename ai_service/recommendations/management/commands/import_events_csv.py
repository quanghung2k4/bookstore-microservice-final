import csv
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from recommendations import graph
from recommendations.models import UserBehaviorEvent


def _parse_ts(raw: str):
    raw = (raw or "").strip()
    if not raw:
        return None

    # CSV format: "2025-01-01 06:23:00" (no timezone)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.isoformat(timespec="seconds")
        except Exception:
            pass

    # Best-effort: let Neo4j try to parse
    return raw


def _neo4j_action(raw_action: str) -> str:
    action = (raw_action or "").strip().lower()
    if action in ("click", "clicked", "view", "viewed"):
        return "VIEWED"
    if action in ("add_to_cart", "added_to_cart", "added-to-cart", "cart_add"):
        return "ADDED_TO_CART"
    if action in ("purchase", "purchased", "bought", "checkout"):
        return "PURCHASED"
    if action in ("search", "searched"):
        return "SEARCHED"
    return ""


def _history_action(raw_action: str) -> str:
    action = (raw_action or "").strip().lower()
    if action in ("click", "clicked", "view", "viewed"):
        return "click"
    if action in ("add_to_cart", "added_to_cart", "added-to-cart", "cart_add"):
        return "add_to_cart"
    if action in ("purchase", "purchased", "bought", "checkout"):
        return "purchase"
    if action in ("search", "searched"):
        return "search"
    return ""


class Command(BaseCommand):
    help = "Import user behavior events from a CSV file into Neo4j (and SQLite history)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            required=True,
            help="Path to CSV (e.g. data_user500.csv)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Neo4j/Django bulk batch size.",
        )
        parser.add_argument(
            "--max-rows",
            type=int,
            default=0,
            help="Optional cap for number of rows (0 = no cap)",
        )
        parser.add_argument(
            "--no-sqlite",
            action="store_true",
            help="Only import into Neo4j, skip saving SQLite UserBehaviorEvent history.",
        )

    def _neo4j_flush(self, driver, rows):
        if not rows:
            return

        with driver.session() as session:
            # Upsert users
            session.run(
                """
                UNWIND $rows AS row
                MERGE (:User {id: row.uid})
                """,
                {"rows": [{"uid": r["uid"]} for r in rows]},
            )

            # Upsert products for non-search events
            product_rows = [
                {"pid": r["pid"]}
                for r in rows
                if r.get("pid") and r.get("action") in ("VIEWED", "ADDED_TO_CART", "PURCHASED")
            ]
            if product_rows:
                session.run(
                    """
                    UNWIND $rows AS row
                    MERGE (:Product {id: row.pid})
                    """,
                    {"rows": product_rows},
                )

            def _ts_expr():
                return "CASE WHEN row.ts IS NULL OR row.ts = '' THEN datetime() ELSE datetime(row.ts) END"

            viewed = [r for r in rows if r.get("action") == "VIEWED" and r.get("pid")]
            if viewed:
                session.run(
                    f"""
                    UNWIND $rows AS row
                    MATCH (u:User {{id: row.uid}})
                    MATCH (p:Product {{id: row.pid}})
                    CREATE (u)-[:VIEWED {{timestamp: {_ts_expr()}, duration: 0}}]->(p)
                    """,
                    {"rows": viewed},
                )

            cart = [r for r in rows if r.get("action") == "ADDED_TO_CART" and r.get("pid")]
            if cart:
                session.run(
                    f"""
                    UNWIND $rows AS row
                    MATCH (u:User {{id: row.uid}})
                    MATCH (p:Product {{id: row.pid}})
                    CREATE (u)-[:ADDED_TO_CART {{timestamp: {_ts_expr()}}}]->(p)
                    """,
                    {"rows": cart},
                )

            purchased = [r for r in rows if r.get("action") == "PURCHASED" and r.get("pid")]
            if purchased:
                session.run(
                    f"""
                    UNWIND $rows AS row
                    MATCH (u:User {{id: row.uid}})
                    MATCH (p:Product {{id: row.pid}})
                    CREATE (u)-[:PURCHASED {{timestamp: {_ts_expr()}, quantity: 1}}]->(p)
                    """,
                    {"rows": purchased},
                )

            searched = [r for r in rows if r.get("action") == "SEARCHED" and r.get("qtext")]
            if searched:
                session.run(
                    f"""
                    UNWIND $rows AS row
                    MATCH (u:User {{id: row.uid}})
                    CREATE (q:Query {{id: randomUUID(), text: row.qtext, timestamp: {_ts_expr()}}})
                    CREATE (u)-[:SEARCHED]->(q)
                    """,
                    {"rows": searched},
                )

    def _sqlite_flush(self, models, *, batch_size: int):
        if not models:
            return 0
        try:
            UserBehaviorEvent.objects.bulk_create(models, batch_size=batch_size)
            return len(models)
        except Exception:
            # fallback to per-row to salvage import
            saved = 0
            for m in models:
                try:
                    m.save()
                    saved += 1
                except Exception:
                    pass
            return saved

    def handle(self, *args, **options):
        file_path = Path(options["file"]).expanduser()
        max_rows = int(options.get("max_rows") or 0)
        batch_size = int(options.get("batch_size") or 1000)
        no_sqlite = bool(options.get("no_sqlite"))

        if not file_path.exists():
            raise SystemExit(f"CSV not found: {file_path}")

        driver = graph.get_driver()
        if driver is None:
            raise SystemExit(
                "Neo4j is unavailable. Start neo4j container and re-run import. "
                f"(NEO4J_URI={getattr(settings, 'NEO4J_URI', '')})"
            )

        counts = {
            "rows": 0,
            "skipped": 0,
            "viewed": 0,
            "added_to_cart": 0,
            "purchased": 0,
            "searched": 0,
            "sqlite_saved": 0,
        }

        neo4j_batch = []
        sqlite_batch = []

        with file_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            expected = {"user_id", "product_id", "action", "timestamp"}
            if not expected.issubset(set(reader.fieldnames or [])):
                raise SystemExit(
                    f"CSV header must include {sorted(expected)}; got {reader.fieldnames}"
                )

            for row in reader:
                if max_rows and counts["rows"] >= max_rows:
                    break

                counts["rows"] += 1
                user_id = (row.get("user_id") or "").strip()
                product_id = (row.get("product_id") or "").strip()
                action_raw = (row.get("action") or "").strip()
                ts = _parse_ts(row.get("timestamp"))

                if not user_id:
                    counts["skipped"] += 1
                    continue

                action = _neo4j_action(action_raw)
                if not action:
                    counts["skipped"] += 1
                    continue

                qtext = None
                pid = product_id or None
                if action == "SEARCHED":
                    # CSV has no query_text column; reuse product_id as a query token.
                    qtext = pid or action_raw
                else:
                    if not pid:
                        counts["skipped"] += 1
                        continue

                neo4j_batch.append({"uid": user_id, "pid": pid, "action": action, "ts": ts, "qtext": qtext})
                if action == "VIEWED":
                    counts["viewed"] += 1
                elif action == "ADDED_TO_CART":
                    counts["added_to_cart"] += 1
                elif action == "PURCHASED":
                    counts["purchased"] += 1
                elif action == "SEARCHED":
                    counts["searched"] += 1

                if not no_sqlite:
                    hist_action = _history_action(action_raw)
                    if hist_action and pid:
                        sqlite_batch.append(
                            UserBehaviorEvent(user_id=str(user_id), product_id=str(pid), action=hist_action)
                        )

                if len(neo4j_batch) >= batch_size:
                    self._neo4j_flush(driver, neo4j_batch)
                    neo4j_batch = []

                    if not no_sqlite and sqlite_batch:
                        counts["sqlite_saved"] += self._sqlite_flush(sqlite_batch, batch_size=batch_size)
                        sqlite_batch = []

                    if counts["rows"] % (batch_size * 5) == 0:
                        self.stdout.write(f"... processed {counts['rows']} rows")

        # Flush remaining
        if neo4j_batch:
            self._neo4j_flush(driver, neo4j_batch)
        if not no_sqlite and sqlite_batch:
            counts["sqlite_saved"] += self._sqlite_flush(sqlite_batch, batch_size=batch_size)

        self.stdout.write(self.style.SUCCESS("Imported CSV into Neo4j"))
        self.stdout.write(str(counts))
