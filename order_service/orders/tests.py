from decimal import Decimal

from django.test import TestCase

from orders.domain.services import calculate_total


class OrderDomainTests(TestCase):
    def test_calculate_total(self):
        total = calculate_total(
            [
                {"quantity": 2, "unit_price": Decimal("10.00")},
                {"quantity": 1, "unit_price": Decimal("5.50")},
            ]
        )
        self.assertEqual(total, Decimal("25.50"))
