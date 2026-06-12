from decimal import Decimal

import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class UserClient:
    def ensure_user(self, user_id):
        response = requests.get(f"{settings.USER_SERVICE_URL}/api/users/{user_id}/profile/", timeout=5)
        if response.status_code != 200:
            raise ValidationError({"user_id": "User not found."})
        return response.json()


class CartClient:
    def get_cart(self, cart_id):
        response = requests.get(f"{settings.CART_SERVICE_URL}/api/carts/{cart_id}/summary/", timeout=5)
        if response.status_code != 200:
            raise ValidationError({"cart_id": "Cart not found."})
        return response.json()

    def clear_cart(self, cart_id):
        """Clear cart after successful checkout"""
        response = requests.post(f"{settings.CART_SERVICE_URL}/api/carts/{cart_id}/clear/", timeout=5)
        if response.status_code not in {200, 204}:
            raise ValidationError({"cart": "Failed to clear cart."})
        return True


class ProductClient:
    def get_product(self, product_id):
        response = requests.get(f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/summary/", timeout=5)
        if response.status_code != 200:
            raise ValidationError({"product_id": "Product not found."})
        payload = response.json()
        payload["price"] = Decimal(str(payload["price"]))
        return payload

    def check_stock(self, items):
        """Check stock availability for multiple items"""
        response = requests.post(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/check_stock/",
            json={"items": items},
            timeout=5
        )
        if response.status_code != 200:
            raise ValidationError({"stock": "Stock check failed."})
        return response.json()

    def reserve_stock(self, product_id, quantity):
        """Reserve stock for a product"""
        response = requests.post(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/reserve_stock/",
            json={"quantity": quantity},
            timeout=5
        )
        if response.status_code != 200:
            raise ValidationError({"stock": f"Failed to reserve stock for product {product_id}."})
        return response.json()

    def release_stock(self, product_id, quantity):
        """Release reserved stock"""
        response = requests.post(
            f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/release_stock/",
            json={"quantity": quantity},
            timeout=5
        )
        if response.status_code != 200:
            raise ValidationError({"stock": f"Failed to release stock for product {product_id}."})
        return response.json()


class PaymentClient:
    def create_payment(self, order_id, amount):
        response = requests.post(
            f"{settings.PAYMENT_SERVICE_URL}/api/payments/",
            json={"order_id": order_id, "amount": str(amount), "method": "cod"},
            timeout=5,
        )
        if response.status_code not in {200, 201}:
            raise ValidationError({"payment": "Payment creation failed."})
        return response.json()


class AIClient:
    def track_purchase(self, *, user_id, product_id, quantity=1):
        """Fire-and-forget purchase event to ai_service to power Neo4j recommendations."""
        try:
            requests.post(
                f"{settings.AI_SERVICE_URL}/api/events/",
                json={
                    "user_id": str(user_id),
                    "product_id": str(product_id),
                    "action": "purchase",
                    "quantity": int(quantity) if quantity is not None else 1,
                },
                timeout=2,
            )
        except Exception:
            # Do not fail checkout if AI service is down
            return False
        return True

