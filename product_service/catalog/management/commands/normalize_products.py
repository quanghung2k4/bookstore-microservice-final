import random
import re
import zlib
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.infrastructure.models import BrandModel, CategoryModel, ProductModel, ProductTypeModel


def _image_url_for_name(name: str) -> str:
    # Derive a deterministic seed from product name.
    lock = zlib.crc32((name or "").encode("utf-8")) % 10000
    # Deterministic real photos (stable per product name).
    # Uses a seeded URL so each product gets a different image without requiring external APIs.
    return f"https://picsum.photos/seed/{lock}/800/600"


def _is_bad_image_url(url: str | None) -> bool:
    if not url:
        return True
    u = url.lower()
    return (
        ("via.placeholder.com" in u)
        or ("placehold.co" in u)
        or ("source.unsplash.com" in u)
    )


class Command(BaseCommand):
    help = "Normalize products to have SKU codes like P0001..P1000 and usable image URLs."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=1000)
        parser.add_argument("--prefix", type=str, default="P")
        parser.add_argument(
            "--create-missing",
            action="store_true",
            help="Create additional products if there are fewer than --count.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-normalization even if products already look normalized.",
        )
        parser.add_argument(
            "--force-images",
            action="store_true",
            help="Force replacing image URLs for normalized products.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Deterministic seed for generated products.",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        prefix: str = options["prefix"]
        create_missing: bool = options["create_missing"]
        force: bool = options["force"]
        force_images: bool = options["force_images"]
        seed: int = options["seed"]

        if count <= 0:
            self.stdout.write(self.style.WARNING("Nothing to do: --count must be > 0"))
            return

        sku_re = re.compile(rf"^{re.escape(prefix)}\d{{4}}$")

        current_total = ProductModel.objects.count()
        target_count = min(count, current_total)
        first_products = list(ProductModel.objects.order_by("id")[:target_count])

        looks_normalized = (
            len(first_products) == target_count
            and all(p.sku == f"{prefix}{i:04d}" for i, p in enumerate(first_products, start=1))
            and all((not _is_bad_image_url(p.image)) for p in first_products)
        )

        if current_total < count and (not create_missing):
            self.stdout.write(
                self.style.WARNING(
                    f"Only {current_total} products exist; will normalize {target_count} (no creation)."
                )
            )

        if (not force) and looks_normalized and (target_count > 0):
            self.stdout.write(self.style.SUCCESS(f"Already normalized: {target_count} products"))
            return

        categories = list(CategoryModel.objects.all().order_by("id"))
        brands = list(BrandModel.objects.all().order_by("id"))
        product_types = list(ProductTypeModel.objects.all().order_by("id"))
        if not categories or not brands or not product_types:
            raise RuntimeError(
                "Missing categories/brands/product types. Run `python manage.py seed_products` first."
            )

        random.seed(seed)

        with transaction.atomic():
            # Re-fetch inside the transaction.
            current_total_in_tx = ProductModel.objects.count()
            target_count_in_tx = min(count, current_total_in_tx)
            products_to_update = list(ProductModel.objects.order_by("id")[:target_count_in_tx])

            # Avoid unique collisions on sku by using temporary values first.
            for idx, product in enumerate(products_to_update, start=1):
                product.sku = f"__tmp__{product.id}__{idx}"
            if products_to_update:
                ProductModel.objects.bulk_update(products_to_update, ["sku"], batch_size=200)

            for idx, product in enumerate(products_to_update, start=1):
                product.sku = f"{prefix}{idx:04d}"
                if force_images or _is_bad_image_url(product.image):
                    product.image = _image_url_for_name(product.name)
                if not sku_re.match(product.sku):
                    raise RuntimeError(f"Generated invalid sku: {product.sku}")
            if products_to_update:
                ProductModel.objects.bulk_update(products_to_update, ["sku", "image"], batch_size=200)

            # Optionally create additional products if we have fewer than requested.
            total_after_updates = ProductModel.objects.count()
            if create_missing and total_after_updates < count:
                to_create = count - total_after_updates
                self.stdout.write(f"Creating {to_create} additional products...")

                new_products = []
                for idx in range(total_after_updates + 1, count + 1):
                    category = categories[(idx - 1) % len(categories)]
                    brand = brands[(idx - 1) % len(brands)]
                    ptype = product_types[(idx - 1) % len(product_types)]

                    name = f"{category.name} {brand.name} Item {idx}"
                    sku = f"{prefix}{idx:04d}"
                    price = Decimal(str(round(random.uniform(5, 2500), 2)))
                    stock = random.randint(0, 500)
                    description = f"Auto-generated product for demo purposes: {name}."

                    new_products.append(
                        ProductModel(
                            name=name,
                            sku=sku,
                            description=description,
                            price=price,
                            stock=stock,
                            image=_image_url_for_name(name),
                            category=category,
                            brand=brand,
                            product_type=ptype,
                            attributes={"normalized": True},
                            is_active=True,
                        )
                    )

                ProductModel.objects.bulk_create(new_products, batch_size=200)

        final_total = ProductModel.objects.count()
        final_target_count = min(count, final_total)
        first_final = list(ProductModel.objects.order_by("id")[:final_target_count])
        ok = (
            len(first_final) == final_target_count
            and all(p.sku == f"{prefix}{i:04d}" for i, p in enumerate(first_final, start=1))
            and all((not _is_bad_image_url(p.image)) for p in first_final)
        )
        if ok:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Normalized OK: updated={final_target_count}, total={final_total}, sku={prefix}0001..{prefix}{final_target_count:04d}"
                )
            )
        else:
            self.stdout.write(self.style.WARNING(f"Normalization finished with warnings: total={final_total}"))
