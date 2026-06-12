from decimal import Decimal
import random
import requests
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from orders.infrastructure.models import OrderModel, OrderItemModel

PRODUCT_API = "http://host.docker.internal:8001/api/products/"

# Load all products
products = []
url = PRODUCT_API

while url:
    print("Loading:", url)

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    products.extend(data.get("results", []))
    url = data.get("next")

print(f"Loaded {len(products)} products")

# Create orders
for i in range(1000):
    order = OrderModel.objects.create(
        user_id=random.randint(1, 200),
        cart_id=random.randint(1, 5000),
        total_price=Decimal("0"),
        status=random.choice(["paid"]),
        payment_reference=f"PAY-{i:06d}",
    )

    total = Decimal("0")

    for _ in range(random.randint(1, 5)):
        p = random.choice(products)

        qty = random.randint(1, 5)
        price = Decimal(str(p["price"]))

        OrderItemModel.objects.create(
            order=order,
            product_id=p["id"],      # VD: P0009
            product_name=p["name"],
            quantity=qty,
            unit_price=price,
        )

        total += price * qty

    order.total_price = total
    order.save(update_fields=["total_price"])

    if (i + 1) % 100 == 0:
        print(f"Created {i + 1} orders")

print("DONE")