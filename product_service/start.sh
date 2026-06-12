#!/bin/sh
set -eu

python manage.py migrate

PRODUCT_COUNT=$(
python manage.py shell -c "from catalog.infrastructure.models import ProductModel; print(ProductModel.objects.count())"
)

if [ "$PRODUCT_COUNT" = "0" ]; then
  echo "Product database is empty. Seeding sample products..."
  python manage.py seed_products
else
  echo "Product database already has $PRODUCT_COUNT products. Skipping seed."
fi

# Normalize existing products: set SKU to P0001.. and ensure image URL is usable.
python manage.py normalize_products --count 1000

python manage.py runserver 0.0.0.0:8001
