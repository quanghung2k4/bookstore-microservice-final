from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PaymentApiTests(APITestCase):
    def test_create_payment(self):
        response = self.client.post(
            reverse("payment-list"),
            {"order_id": 1, "amount": "10.00", "method": "cod"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
