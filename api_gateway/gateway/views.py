import json
import time
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


SERVICE_MAP = {
    "products": settings.PRODUCT_SERVICE_URL,
    "carts": settings.CART_SERVICE_URL,
    "orders": settings.ORDER_SERVICE_URL,
    "users": settings.USER_SERVICE_URL,
    "payments": settings.PAYMENT_SERVICE_URL,
    "shipping": settings.SHIPPING_SERVICE_URL,
    "ai": settings.AI_SERVICE_URL,
}


def _proxy_request(request_method, url, *, params=None, payload=None, service=None):
    attempts = 3 if service == "ai" else 1
    delay_seconds = 1
    last_error = None

    for attempt in range(attempts):
        try:
            return request_method(url, params=params, json=payload, timeout=10)
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            time.sleep(delay_seconds)

    raise last_error


@method_decorator(csrf_exempt, name='dispatch')
class ProxyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
            
        service = kwargs["service"]
        path = kwargs.get("path", "")
        base_url = SERVICE_MAP.get(service)
        if not base_url:
            return JsonResponse({"detail": "Service not found."}, status=404)

        url = f"{base_url}/api/{path}"
        request_method = getattr(requests, request.method.lower())
        
        # Use request.GET for query parameters
        query_params = request.GET.dict()
        
        # Get request data
        payload = None
        if request.method in {"POST", "PUT", "PATCH"}:
            if request.body:
                try:
                    payload = json.loads(request.body)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    try:
                        payload = json.loads(request.body.decode(request.encoding or "utf-8", errors="replace"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        payload = None
                except TypeError:
                    payload = None
        
        try:
            response = _proxy_request(
                request_method,
                url,
                params=query_params,
                payload=payload,
                service=service,
            )
            try:
                data = response.json()
            except ValueError:
                data = {"detail": response.text}
            
            # Create JSON response with CORS headers
            json_response = JsonResponse(data, status=response.status_code, safe=False)
            json_response["Access-Control-Allow-Origin"] = "*"
            json_response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            json_response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return json_response
            
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"detail": f"Service unavailable: {str(e)}"}, 
                status=503
            )
