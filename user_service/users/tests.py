from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
    def test_create_customer(self):
        response = self.client.post(
            reverse("user-list"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
                "role": "customer",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "customer")

    def test_login(self):
        user = get_user_model().objects.create(username="bob", email="bob@example.com", role="customer")
        user.set_password("secret123")
        user.save()

        response = self.client.post(
            reverse("user-login"),
            {"username": "bob", "password": "secret123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "bob")
