from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from carts.infrastructure.models import CartModel


class CartApiTests(APITestCase):
    @patch("carts.infrastructure.clients.UserClient.ensure_user")
    def test_create_cart(self, _ensure_user):
        # External user validation is mocked for isolated service testing.
        response = self.client.post(reverse("cart-list"), {"user_id": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartModel.objects.count(), 1)
