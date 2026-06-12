import json
import logging
import time
from collections import Counter

import requests
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from . import graph, lstm_model, rag_chatbot
from .etl import run_full_etl
from .models import UserBehaviorEvent
from .lstm_model import lstm_predictor

logger = logging.getLogger(__name__)


_PRODUCT_CACHE_TTL_SECONDS = 300
_product_cache = {}


def _get_product_detail(product_id):
    """Best-effort fetch from Product Service.

    Returns a dict with keys: id, name, price, category_id, category_name.
    """

    if product_id is None:
        return None

    pid = str(product_id)
    now = time.monotonic()
    cached = _product_cache.get(pid)
    if cached and cached[0] > now:
        return cached[1]

    try:
        r = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/{pid}/",
            timeout=1.5,
        )
        if r.status_code != 200:
            return None
        data = r.json() or {}
        category_id = data.get("category")
        category_detail = data.get("category_detail") or {}
        category_name = ""
        category_slug = ""
        if isinstance(category_detail, dict):
            category_name = category_detail.get("name", "") or ""
            category_slug = category_detail.get("slug", "") or ""
            # prefer nested id if present
            if category_detail.get("id") is not None:
                category_id = category_detail.get("id")

        detail = {
            "id": str(data.get("id", pid)),
            "name": data.get("name", "") or "",
            "price": data.get("price", 0) or 0,
            "category_id": str(category_id) if category_id is not None else "",
            "category_name": category_name,
            "category_slug": category_slug,
        }
        _product_cache[pid] = (now + _PRODUCT_CACHE_TTL_SECONDS, detail)
        return detail
    except Exception:
        return None


def _fallback_category_products(user_id, limit: int):
    """Personalized fallback: products from the same category as user's latest action."""

    if not user_id:
        return []

    try:
        recent = list(
            UserBehaviorEvent.objects.filter(user_id=str(user_id))
            .order_by("-created_at")
            .only("product_id", "action", "created_at")[:50]
        )
    except Exception:
        recent = []

    if not recent:
        return []

    def _w(a: str) -> int:
        v = (a or "").strip().lower()
        if v in ("purchase", "purchased", "bought", "checkout"):
            return 3
        if v in ("add_to_cart", "added_to_cart", "added-to-cart", "cart_add"):
            return 2
        # click/view
        if v in ("click", "view", "viewed"):
            return 1
        return 0

    seed_pid = None
    best = -1
    for ev in recent:
        pid = getattr(ev, "product_id", None)
        if not pid:
            continue
        w = _w(getattr(ev, "action", ""))
        if w > best:
            best = w
            seed_pid = pid
            if best >= 3:
                break

    if not seed_pid:
        return []

    seed = _get_product_detail(seed_pid)
    if not seed:
        return []

    slug = (seed.get("category_slug") or "").strip()
    cat_id = (seed.get("category_id") or "").strip()
    if not slug and not cat_id:
        return []

    # Prefer slug because frontend already uses it.
    params = f"?page_size={limit + 1}"
    if slug:
        params += f"&category={requests.utils.quote(slug)}"
    else:
        params += f"&category={requests.utils.quote(cat_id)}"

    try:
        r = requests.get(f"{settings.PRODUCT_SERVICE_URL}/api/products/{params}", timeout=2)
        if r.status_code != 200:
            return []
        data = r.json()
    except Exception:
        return []

    items = _as_list(data)
    results = []
    for p in items:
        pid = p.get("id")
        if pid is None:
            continue
        if str(pid) == str(seed.get("id")):
            continue
        results.append({"product_id": str(pid), "score": 1, "source": "category"})
        if len(results) >= limit:
            break

    return results


def _upsert_product_enriched(product_id):
    """Upsert Product + Category relationship when possible."""

    detail = _get_product_detail(product_id)
    if not detail:
        graph.upsert_product(product_id)
        return

    graph.upsert_product(
        product_id=detail["id"],
        name=detail.get("name", ""),
        category=detail.get("category_name", ""),
        price=detail.get("price", 0) or 0,
    )

    cat_id = detail.get("category_id")
    if cat_id:
        graph.upsert_category(cat_id, detail.get("category_name", ""))
        graph.link_product_category(detail["id"], cat_id)


def _clamp_int(value, *, default: int, min_value: int, max_value: int) -> int:
    try:
        value_int = int(value)
    except Exception:
        return default
    return max(min_value, min(max_value, value_int))


def _as_list(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("results", [])
    return []


def _best_sellers_from_orders(limit: int):

    limit = _clamp_int(limit, default=8, min_value=1, max_value=50)
    url = f"{settings.ORDER_SERVICE_URL}/api/orders/"
    counts: Counter[str] = Counter()

    for _ in range(5):  # cap pagination to avoid heavy requests
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                break
            data = r.json()
        except Exception as e:
            logger.warning(f"Best-seller fallback failed fetching orders: {e}")
            break

        for order in _as_list(data):
            for item in (order.get("items") or []):
                pid = item.get("product_id")
                if pid is None:
                    continue
                qty = item.get("quantity", 1)
                try:
                    qty_int = int(qty)
                except Exception:
                    qty_int = 1
                counts[str(pid)] += max(1, qty_int)

        next_url = data.get("next") if isinstance(data, dict) else None
        if not next_url:
            break
        url = next_url

    if not counts:
        return []

    return [
        {"product_id": pid, "score": score, "source": "bestseller"}
        for pid, score in counts.most_common(limit)
    ]


def _fallback_newest_products(limit: int):
    """Last-resort fallback using Product Service newest products."""
    limit = _clamp_int(limit, default=8, min_value=1, max_value=50)
    try:
        r = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/?ordering=-created_at&page_size={limit}",
            timeout=5,
        )
        if r.status_code != 200:
            return []
        data = r.json()
        items = _as_list(data)
        results = []
        for p in items:
            pid = p.get("id")
            if pid is None:
                continue
            results.append({"product_id": str(pid), "score": 1, "source": "newest"})
        return results[:limit]
    except Exception as e:
        logger.warning(f"Newest-products fallback failed: {e}")
        return []


def _dedupe_recommendations(results, limit: int):
    seen = set()
    unique = []
    for r in results or []:
        pid = r.get("product_id")
        if pid is None:
            continue
        pid_str = str(pid)
        if pid_str in seen:
            continue
        seen.add(pid_str)
        item = dict(r)
        item["product_id"] = pid_str
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique


def _body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}


def _normalize_action(raw_action: str) -> str:
    if not raw_action:
        return ""
    action = str(raw_action).strip().lower()
    if action in ("click", "clicked", "view", "viewed"):
        return "click"
    if action in ("add_to_cart", "added_to_cart", "added-to-cart", "cart_add"):
        return "add_to_cart"
    if action in ("purchase", "purchased", "bought", "checkout"):
        return "purchase"
    return action


def _neo4j_action(raw_action: str) -> str:
    """Map various client actions into the Neo4j event vocabulary used by graph.py."""
    action = _normalize_action(raw_action)
    if action == "click":
        return "VIEWED"
    if action == "add_to_cart":
        return "ADDED_TO_CART"
    if action == "purchase":
        return "PURCHASED"
    if action in ("searched", "search"):
        return "SEARCHED"
    return str(raw_action).strip().upper() if raw_action else "VIEWED"


@method_decorator(csrf_exempt, name="dispatch")
class TrackEventView(View):
    """POST /api/events/ — record user behavior event into Neo4j."""

    def post(self, request):
        data = _body(request)
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        raw_action = data.get("action", "view")
        action = _neo4j_action(raw_action)
        duration = data.get("duration", 0)
        query_text = data.get("query_text", "")

        if not user_id:
            return JsonResponse({"detail": "user_id required"}, status=400)

        # graph.upsert_user(user_id)

        # if action == "SEARCHED" and query_text:
        #     graph.record_search(user_id, query_text)
        # elif product_id:
            # _upsert_product_enriched(product_id)
            # if action == "VIEWED":
            #     graph.record_view(user_id, product_id, duration)
            # elif action == "ADDED_TO_CART":
            #     graph.record_cart_add(user_id, product_id)
            # elif action == "PURCHASED":
            #     graph.record_purchase(user_id, product_id, data.get("quantity", 1))

            # Also persist into SQLite for predictor.py usage
        hist_action = _normalize_action(raw_action)
        if hist_action:
            UserBehaviorEvent.objects.create(
                user_id=str(user_id),
                product_id=str(product_id),
                action=hist_action,
            )

        return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class UserHistoryView(View):
    """GET/POST /api/history/ — store and retrieve user history for predictor.py."""

    def get(self, request):
        user_id = request.GET.get("user_id")
        limit = int(request.GET.get("limit", 10))

        if not user_id:
            return JsonResponse({"detail": "user_id required"}, status=400)

        qs = (
            UserBehaviorEvent.objects.filter(user_id=str(user_id))
            .order_by("-created_at")
            .only("product_id", "action", "created_at")
        )
        events = list(qs[: max(1, min(limit, 50))])
        events.reverse()  # chronological

        history = [{"product_id": e.product_id, "action": e.action, "create_at":e.created_at} for e in events]
        return JsonResponse({"user_id": user_id, "history": history})

    def post(self, request):
        data = _body(request)
        user_id = data.get("user_id")
        product_id = data.get("product_id")
        action = _normalize_action(data.get("action", ""))

        if not user_id:
            return JsonResponse({"detail": "user_id required"}, status=400)
        if not product_id:
            return JsonResponse({"detail": "product_id required"}, status=400)
        if not action:
            return JsonResponse({"detail": "action required"}, status=400)

        UserBehaviorEvent.objects.create(
            user_id=str(user_id),
            product_id=str(product_id),
            action=action,
        )
        return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class RecommendView(View):
    """GET /api/recommendations/?user_id=X&strategy=hybrid&limit=10"""

    def _compute(self, *, user_id, strategy: str, limit: int):
        results = []

        if strategy in ("collaborative", "hybrid") and user_id:
            results += graph.get_collaborative_recommendations(user_id, limit=limit)

        if strategy in ("content", "hybrid") and user_id:
            results += graph.get_content_based_recommendations(user_id, limit=limit)

        # Personalized fallback (based on user's latest action history)
        if user_id and (not results) and strategy in ("content", "collaborative", "hybrid"):
            results = _fallback_category_products(user_id, limit)

        if strategy == "trending" or not results:
            results = graph.get_trending_products(limit=limit)

        # Fallback: bestseller from Order Service
        if not results:
            results = _best_sellers_from_orders(limit)

        # Last resort: newest products from Product Service
        if not results:
            results = _fallback_newest_products(limit)

        # LSTM boost — prepend LSTM predictions (currently a no-op placeholder)
        if user_id:
            behavior_seq = graph.get_user_behavior_sequence(user_id, limit=50)
            lstm_pids = lstm_model.predict(behavior_seq, top_k=5)
            lstm_items = [{"product_id": pid, "source": "lstm", "score": 100} for pid in lstm_pids]
            results = lstm_items + (results or [])

        return _dedupe_recommendations(results, limit)

    def _ingest_events(self, *, user_id, events):
        if not user_id or not isinstance(events, list) or not events:
            return

        graph.upsert_user(user_id)

        for ev in events[:200]:  # safety cap
            if not isinstance(ev, dict):
                continue

            product_id = ev.get("product_id")
            raw_action = ev.get("action") or ev.get("event") or "VIEWED"
            duration = ev.get("duration", 0)
            query_text = ev.get("query_text", "")
            quantity = ev.get("quantity", 1)

            action = _neo4j_action(raw_action)

            if action == "SEARCHED" and query_text:
                graph.record_search(user_id, query_text)
                continue

            if product_id is None:
                continue

            _upsert_product_enriched(product_id)
            if action == "VIEWED":
                graph.record_view(user_id, product_id, duration)
            elif action == "ADDED_TO_CART":
                graph.record_cart_add(user_id, product_id)
            elif action == "PURCHASED":
                graph.record_purchase(user_id, product_id, quantity)

            hist_action = _normalize_action(raw_action)
            if hist_action:
                try:
                    UserBehaviorEvent.objects.create(
                        user_id=str(user_id),
                        product_id=str(product_id),
                        action=hist_action,
                    )
                except Exception:
                    # Don't fail recommendation due to history persistence errors
                    pass

    def get(self, request):
        user_id = request.GET.get("user_id")
        strategy = request.GET.get("strategy", "hybrid")
        limit = _clamp_int(request.GET.get("limit", 10), default=10, min_value=1, max_value=50)
        try:
            # 2. Gọi hàm nội bộ lấy dữ liệu sản phẩm bán chạy từ Order Service
            recs = _best_sellers_from_orders(limit)
        except Exception as e:
            recs = []
        if not recs:
            recs = _fallback_newest_products(limit)

        return JsonResponse({"recommendations": recs})

    def post(self, request):
        """
        POST /api/recommendations/ — CHỈ lấy gợi ý chuỗi hành vi từ mô hình LSTM độc lập.
        """
        print("POST CALLED")
        try:
            data = _body(request)  # Hàm helper parse body JSON của bạn
        except Exception:
            return JsonResponse({"error": "Định dạng JSON không hợp lệ"}, status=400)
            
        user_id = data.get("user_id")

        # Lấy limit (số lượng sản phẩm cần mô hình LSTM sinh ra tự hồi quy, mặc định là 20)
        limit = _clamp_int(data.get("limit", 20), default=20, min_value=1, max_value=50)

        # Hỗ trợ cả 2 key 'events' và 'history' từ client gửi lên
        events = data.get("events")
        if events is None:
            events = data.get("history", [])

        # Nếu client không truyền chuỗi hành vi mới, lấy lịch sử cũ từ SQLite làm tín hiệu đầu vào cho LSTM
        if (not events) and user_id:
            try:
                qs =  UserBehaviorEvent.objects.filter(user_id=str(user_id)).order_by("-created_at").only("product_id")
                
                stored = list(qs[:20]) # Lấy tối đa chuỗi gần nhất
                stored.reverse()
                events = [{"product_id": e.product_id} for e in stored]
            except Exception:
                events = []
    
        user_past_clicks = []
        for ev in events:
            if isinstance(ev, dict) and ev.get("product_id"):
                user_past_clicks.append(str(ev.get("product_id")))
            elif isinstance(ev, str):
                user_past_clicks.append(ev)

        # KIỂM TRA ĐẦU VÀO: Nếu hoàn toàn không có lịch sử clicks nào để dự đoán
        if not user_past_clicks:
            return JsonResponse({
                "recommendations": [],
                "user_id":user_id, 
                "remark": "Không có đủ dữ liệu chuỗi hành vi để chạy mô hình LSTM.",
                "debug": "I AM HERE"
            })

        # GỌI DUY NHẤT TỪ FILE lstm_model.py (Bỏ hoàn toàn _compute và các fallback khác)
        try:
            predicted_pids = lstm_predictor.predict_sequence(
                user_history_list=user_past_clicks, 
                num_predictions=limit
            )
            
            # Format kết quả đầu ra theo chuẩn API cấu trúc cũ của bạn
            recs = [{"product_id": pid} for pid in predicted_pids]
            
        except Exception as e:
            # Đảm bảo API không sập hoàn toàn nếu lỗi phần cứng Tensor/Cuda
            return JsonResponse({"error": f"LSTM Model Service Error: {str(e)}"}, status=500)

        return JsonResponse({"recommendations": recs})


@method_decorator(csrf_exempt, name="dispatch")
class SearchView(View):
    """GET /api/search/?q=query&user_id=X"""

    def get(self, request):
        query = request.GET.get("q", "")
        user_id = request.GET.get("user_id")
        limit = int(request.GET.get("limit", 10))

        if not query:
            return JsonResponse({"results": []})

        # Record search event
        if user_id:
            graph.record_search(user_id, query)

        results = graph.search_products_by_query(query, limit=limit)
        return JsonResponse({"results": results, "query": query})


@method_decorator(csrf_exempt, name="dispatch")
class ChatView(View):
    """POST /api/chat/ — RAG chatbot endpoint."""

    def post(self, request):
        data = _body(request)
        message = data.get("message", "").strip()
        user_id = data.get("user_id")
        history = data.get("history", [])

        if not message:
            return JsonResponse({"detail": "message required"}, status=400)

        response = rag_chatbot.chat(message, user_id=user_id, conversation_history=history)
        return JsonResponse(response)


@method_decorator(csrf_exempt, name="dispatch")
class HealthView(View):
    """GET /api/health/ — lightweight readiness probe."""

    def get(self, request):
        return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, name="dispatch")
class ETLView(View):
    """POST /api/etl/ — trigger full ETL sync."""

    def post(self, request):
        result = run_full_etl()
        return JsonResponse(result)

@csrf_exempt
def get_recommendation(request):
    if request.method == 'POST':
        try:
            # Import predictor lazily to avoid importing torch for unrelated commands/endpoints
            from models.predictor import get_ai_predictor

            # Nhận lịch sử hành vi từ Frontend (React/Vue/Android) gửi lên
            body = _body(request)
            user_history = body.get('history', [])
            user_id = body.get('user_id')
            limit = int(body.get('limit', 5))

            if not user_history and user_id:
                qs = (
                    UserBehaviorEvent.objects.filter(user_id=str(user_id))
                    .order_by('-created_at')
                    .only('product_id', 'action', 'created_at')
                )
                events = list(qs[: max(1, min(limit, 50))])
                events.reverse()
                user_history = [{"product_id": e.product_id, "action": e.action} for e in events]
            
            if not user_history:
                return JsonResponse({'error': 'Lịch sử trống'}, status=400)
            
            # Gọi AI dự đoán chỉ mất vài mili-giây
            recommended_product = get_ai_predictor().predict(user_history)
            
            return JsonResponse({
                'status': 'success',
                'suggested_item': recommended_product
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Chỉ chấp nhận method POST'}, status=405)