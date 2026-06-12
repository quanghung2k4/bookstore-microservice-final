import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


class ProductClient:
    def ensure_product(self, product_id):
        response = requests.get(f"{settings.PRODUCT_SERVICE_URL}/api/products/{product_id}/summary/", timeout=5)
        if response.status_code != 200:
            raise ValidationError({"product_id": "Product not found."})
        return response.json()


class UserClient:
    def ensure_user(self, user_id):
        response = requests.get(f"{settings.USER_SERVICE_URL}/api/users/{user_id}/profile/", timeout=5)
        if response.status_code != 200:
            raise ValidationError({"user_id": "User not found."})
        return response.json()

