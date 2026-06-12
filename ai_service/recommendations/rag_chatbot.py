"""
RAG Chatbot — rule-based fallback khi không có OpenAI key.
Trả lời tiếng Việt, dựa trên sản phẩm lấy từ Neo4j + product_service.
"""

import logging
import re
import requests
from django.conf import settings
from . import graph

logger = logging.getLogger(__name__)

# ── Fetch helpers ─────────────────────────────────────────────────────────────

def _fetch_products(product_ids):
    products = []
    for pid in product_ids[:8]:
        try:
            r = requests.get(f"{settings.PRODUCT_SERVICE_URL}/api/products/{pid}/", timeout=3)
            if r.status_code == 200:
                products.append(r.json())
        except Exception:
            pass
    return products


def _fetch_trending_products(limit=6):
    try:
        r = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/?page_size={limit}&ordering=-created_at",
            timeout=3,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("results", data) if isinstance(data, dict) else data
    except Exception:
        pass
    return []


def _extract_keyword(query):
    """Trích từ khóa sản phẩm, map tiếng Việt → tiếng Anh nếu cần."""
    # Map từ tiếng Việt phổ biến sang keyword tiếng Anh trong DB
    vi_to_en = {
        "sách": "book", "sach": "book",
        "điện thoại": "phone", "dien thoai": "phone",
        "laptop": "laptop", "máy tính": "laptop", "may tinh": "laptop",
        "tai nghe": "headphone", "headphone": "headphone",
        "tivi": "tv", "ti vi": "tv", "màn hình": "tv",
        "đồng hồ": "watch", "dong ho": "watch",
        "giày": "sneaker", "giay": "sneaker", "sneaker": "sneaker",
        "quần": "jeans", "quan": "jeans", "áo": "shirt", "ao": "shirt",
        "váy": "dress", "vay": "dress",
        "xe đạp": "bicycle", "xe dap": "bicycle",
        "thể thao": "sport", "the thao": "sport",
        "đồ chơi": "lego", "do choi": "lego", "lego": "lego",
        "thú cưng": "pet", "thu cung": "pet", "chó": "dog", "cho": "dog",
        "mèo": "cat", "meo": "cat",
        "ô tô": "car", "xe hoi": "car", "lốp": "tire",
        "mỹ phẩm": "loreal", "my pham": "loreal", "son": "makeup",
        "thực phẩm": "nestle", "thuc pham": "nestle", "đồ ăn": "nestle",
        "camera": "camera", "máy ảnh": "camera", "may anh": "camera",
        "máy tính bảng": "ipad", "may tinh bang": "ipad", "ipad": "ipad",
        "samsung": "samsung", "apple": "apple", "iphone": "iphone",
        "nike": "nike", "adidas": "adidas",
    }

    q = query.lower()

    # Thử match cụm từ trước
    for vi, en in vi_to_en.items():
        if vi in q:
            return en

    stop_words = {
        "gợi", "ý", "goi", "cho", "tôi", "toi", "tốt", "nhất", "tot", "nhat",
        "tư", "vấn", "van", "mua", "cần", "can", "muốn", "muon",
        "recommend", "suggest", "best", "good", "tìm", "tim",
        "có", "co", "nào", "nao", "loại", "loai", "sản", "phẩm", "san", "pham",
        "giá", "rẻ", "gia", "re", "đắt", "dat", "bạn", "ban", "ơi", "oi",
        "nhé", "nhe", "nên", "nen", "hãy", "hay", "được", "duoc", "với", "voi",
        "một", "mot", "các", "cac", "những", "nhung", "và", "va", "là", "la",
        "bán", "ban", "chạy", "chay", "hiện", "hien", "tại", "tai",
        "hay", "nhất", "nhat", "mới", "moi", "phổ", "pho", "biến", "bien",
    }
    words = q.split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    if keywords:
        keywords.sort(key=len, reverse=True)
        return keywords[0]
    return query[:20]


def _search_products_by_keyword(keyword, limit=6):
    try:
        r = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/?search={keyword}&page_size={limit}",
            timeout=3,
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("results", data) if isinstance(data, dict) else data
    except Exception:
        pass
    return []


def _contains_phrase(text, phrases):
    normalized = f" {text.lower()} "
    for phrase in phrases:
        candidate = phrase.lower().strip()
        if " " in candidate:
            if candidate in text.lower():
                return True
        elif f" {candidate} " in normalized:
            return True
    return False


def _text_blob(product):
    category = product.get("category_detail") or {}
    brand = product.get("brand_detail") or {}
    product_type = product.get("product_type_detail") or {}
    parts = [
        product.get("name", ""),
        product.get("description", ""),
        category.get("name", "") if isinstance(category, dict) else "",
        brand.get("name", "") if isinstance(brand, dict) else "",
        product_type.get("name", "") if isinstance(product_type, dict) else "",
    ]
    return " ".join(str(part).lower() for part in parts if part)


def _detect_query_profile(query):
    q = query.lower()
    profile = {
        "label": "san pham",
        "must_match": [],
        "prefer": [],
    }

    if any(token in q for token in ["sach", "sách", "book", "tieu thuyet", "truyen", "truyện"]):
        profile["label"] = "sach"
        profile["must_match"] = ["book", "books"]
        profile["prefer"] = ["book", "books", "author", "penguin", "clean code", "pragmatic", "atomic habits"]
        return profile

    if any(token in q for token in ["laptop", "macbook", "notebook"]):
        profile["label"] = "laptop"
        profile["must_match"] = ["laptop"]
        profile["prefer"] = ["laptop", "notebook", "macbook"]
        return profile

    if any(token in q for token in ["dien thoai", "điện thoại", "phone", "iphone", "smartphone"]):
        profile["label"] = "dien thoai"
        profile["must_match"] = ["phone", "smartphone", "iphone"]
        profile["prefer"] = ["phone", "smartphone", "iphone", "samsung", "apple"]
        return profile

    if any(token in q for token in ["tivi", "ti vi", "tv", "television"]):
        profile["label"] = "tv"
        profile["must_match"] = ["tv", "television"]
        profile["prefer"] = ["tv", "television", "qled", "oled", "smart tv"]
        return profile

    return profile


def _rank_products_for_query(products, query):
    profile = _detect_query_profile(query)
    scored = []

    for product in products:
        blob = _text_blob(product)
        score = 0

        for token in profile["prefer"]:
            if token in blob:
                score += 3

        if any(token in blob for token in profile["must_match"]):
            score += 8
        elif profile["must_match"]:
            continue

        name = str(product.get("name", "")).lower()
        if query.lower() in name:
            score += 5

        words = [word for word in re.split(r"\W+", query.lower()) if len(word) > 2]
        for word in words:
            if word in blob:
                score += 1

        scored.append((score, product))

    scored.sort(
        key=lambda item: (
            item[0],
            float(item[1].get("stock", 0) or 0),
            -float(item[1].get("price", 0) or 0),
        ),
        reverse=True,
    )
    return [product for score, product in scored if score > 0]


# ── Formatting ────────────────────────────────────────────────────────────────

def _product_summary(p):
    cat = p.get("category_detail") or {}
    cat_name = cat.get("name", "") if isinstance(cat, dict) else ""
    brand = p.get("brand_detail") or {}
    brand_name = brand.get("name", "") if isinstance(brand, dict) else ""
    description = re.sub(r"\s+", " ", str(p.get("description", "")).strip())
    short_description = description[:90].rstrip()
    return "\n".join(
        [
            f"- {p.get('name')}",
            f"  Thuong hieu: {brand_name or 'Dang cap nhat'}",
            f"  Gia: ${p.get('price')}",
            f"  Danh muc: {cat_name or 'Khac'} | Con hang: {p.get('stock')}",
            f"  Mo ta: {short_description or 'Chua co mo ta.'}",
        ]
    )


def _build_context(products):
    return "\n".join(_product_summary(p) for p in products)


# ── Rule-based Vietnamese response ────────────────────────────────────────────

def _rule_based_answer(query, products):
    q = query.lower()
    product_list = "\n\n".join(_product_summary(p) for p in products[:5]) if products else ""
    profile = _detect_query_profile(query)

    if not products:
        if profile["label"] == "sach":
            return "Toi chua tim thay sach phu hop. Ban thu tim voi tu khoa cu the hon, vi du: sach lap trinh, sach kinh doanh."
        return "Toi chua tim thay san pham phu hop. Ban thu mo ta cu the hon nhu muc gia, thuong hieu hoac danh muc."

    if _contains_phrase(q, ["xin chào", "hello", "hi", "chào", "alo", "hey"]):
        return f"Xin chào! Tôi là trợ lý mua sắm AI 🤖\nTôi có thể giúp bạn tìm sản phẩm, so sánh giá, hoặc gợi ý phù hợp với nhu cầu.\n\nMột số sản phẩm nổi bật:\n{product_list}"

    if _contains_phrase(q, ["đơn hàng", "order", "tài khoản", "account", "giao hàng", "shipping", "vận chuyển"]):
        return "Tôi chỉ hỗ trợ tìm kiếm và tư vấn sản phẩm. Để xem đơn hàng, bạn vui lòng vào mục 'Đơn hàng' trên menu nhé! 😊"

    if any(w in q for w in ["rẻ", "giá rẻ", "cheap", "affordable", "budget", "tiết kiệm", "ít tiền"]):
        cheap = sorted(products, key=lambda p: float(p.get("price", 0)))
        return "Cac lua chon gia tot nhat:\n\n" + "\n\n".join(_product_summary(p) for p in cheap[:5])

    if any(w in q for w in ["đắt", "cao cấp", "premium", "luxury", "xịn", "chất lượng cao"]):
        expensive = sorted(products, key=lambda p: float(p.get("price", 0)), reverse=True)
        return "Cac lua chon cao cap:\n\n" + "\n\n".join(_product_summary(p) for p in expensive[:5])

    if any(w in q for w in ["gợi ý", "recommend", "suggest", "nên mua", "tốt nhất", "best", "tư vấn"]):
        if profile["label"] == "sach":
            return f"Neu ban dang tim sach hay, day la cac tua phu hop nhat toi loc duoc:\n\n{product_list}"
        return f"Day la cac san pham phu hop nhat voi nhu cau cua ban:\n\n{product_list}"

    if any(w in q for w in ["phổ biến", "trending", "hot", "bán chạy", "nổi bật", "popular"]):
        if profile["label"] == "sach":
            return f"Cac cuon sach dang noi bat trong kho hien tai:\n\n{product_list}"
        return f"Cac san pham dang duoc quan tam nhieu:\n\n{product_list}"

    if profile["label"] == "sach":
        return f"Toi tim thay cac cuon sach sau:\n\n{product_list}"
    return f"Toi tim thay cac san pham sau:\n\n{product_list}"


# ── LLM call ──────────────────────────────────────────────────────────────────

def _call_llm(system_prompt, user_message):
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=512,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None


# ── Main entry ────────────────────────────────────────────────────────────────

def chat(user_message, user_id=None, conversation_history=None):
    """Returns {answer, products, sources}"""

    # 1. Try Neo4j graph (non-blocking — nếu Neo4j down thì bỏ qua)
    graph_recs = []
    try:
        if user_id:
            graph_recs += graph.get_collaborative_recommendations(user_id, limit=5)
            graph_recs += graph.get_content_based_recommendations(user_id, limit=5)
        if not graph_recs:
            graph_recs = graph.get_trending_products(limit=8)
        search_recs = graph.search_products_by_query(user_message, limit=5)
        graph_recs = search_recs + graph_recs
    except Exception:
        graph_recs = []

    seen, unique_recs = set(), []
    for r in graph_recs:
        pid = r.get("product_id")
        if pid and pid not in seen:
            seen.add(pid)
            unique_recs.append(r)

    products = _fetch_products([r["product_id"] for r in unique_recs[:8]])

    # 2. Keyword search — luôn chạy để bổ sung sản phẩm liên quan
    keyword = _extract_keyword(user_message)
    if len(keyword) > 2:
        keyword_products = _search_products_by_keyword(keyword, limit=6)
        existing_ids = {p["id"] for p in products}
        relevant = [p for p in keyword_products if p["id"] not in existing_ids]
        products = relevant + products

    ranked_products = _rank_products_for_query(products, user_message)
    if ranked_products:
        products = ranked_products

    products = products[:8]

    # 3. Trending fallback nếu vẫn trống
    if not products:
        products = _fetch_trending_products(limit=6)
        ranked_products = _rank_products_for_query(products, user_message)
        if ranked_products:
            products = ranked_products

    # 4. Generate answer
    llm_answer = None
    if settings.OPENAI_API_KEY:
        context = _build_context(products)
        system_prompt = f"""Bạn là trợ lý mua sắm AI cho một cửa hàng thương mại điện tử.
Hãy trả lời bằng tiếng Việt, thân thiện và ngắn gọn (dưới 200 từ).
Nếu được hỏi về sản phẩm, hãy đề cập tên và giá cụ thể.
Nếu được hỏi về đơn hàng hoặc tài khoản, hãy nói bạn chỉ hỗ trợ tìm kiếm sản phẩm.

Sản phẩm hiện có:
{context if context else "Chưa có sản phẩm cụ thể."}"""
        llm_answer = _call_llm(system_prompt, user_message)

    answer = llm_answer if llm_answer else _rule_based_answer(user_message, products)

    return {
        "answer": answer,
        "products": products[:5],
        "sources": [r.get("product_id") for r in unique_recs[:5]],
    }
