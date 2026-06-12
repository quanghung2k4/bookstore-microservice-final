from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.infrastructure.models import BrandModel, CategoryModel, ProductModel, ProductTypeModel


class ProductApiTests(APITestCase):
    def setUp(self):
        self.category = CategoryModel.objects.create(name="Phone", slug="phone")
        self.brand = BrandModel.objects.create(name="Acme")
        self.product_type = ProductTypeModel.objects.create(name="Electronics")
        ProductModel.objects.create(
            name="Acme Phone X",
            sku="PHONE-X",
            description="Flagship phone",
            price=Decimal("999.99"),
            stock=10,
            category=self.category,
            brand=self.brand,
            product_type=self.product_type,
            attributes={"ram": "16GB", "color": "black"},
        )

    def test_list_products(self):
        response = self.client.get(reverse("product-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_filter_by_category_slug(self):
        response = self.client.get(reverse("product-list"), {"category": "phone"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
