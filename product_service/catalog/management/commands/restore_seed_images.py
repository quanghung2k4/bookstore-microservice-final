import ast
from pathlib import Path
import re
import zlib

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.infrastructure.models import ProductModel


def _fallback_image_url(name: str) -> str:
    # Derive a deterministic seed from product name.
    _ = re.findall(r"[a-zA-Z0-9]+", (name or "").lower())
    lock = zlib.crc32((name or "").encode("utf-8")) % 10000
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


def _load_seed_name_to_image() -> dict[str, str]:
    seed_file = Path(__file__).resolve().parent / "seed_products.py"
    source = seed_file.read_text(encoding="utf-8")
    tree = ast.parse(source)
    mapping: dict[str, str] = {}

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call):
            try:
                func = node.func
                if not isinstance(func, ast.Attribute) or func.attr != "_make":
                    return
                if not node.args:
                    return
                arg0 = node.args[0]
                if not isinstance(arg0, ast.Dict):
                    return

                values: dict[str, str] = {}
                for k, v in zip(arg0.keys, arg0.values):
                    if isinstance(k, ast.Constant) and isinstance(k.value, str) and isinstance(v, ast.Constant) and isinstance(v.value, str):
                        values[k.value] = v.value
                name = values.get("name")
                image = values.get("image")
                if name and image:
                    mapping[name] = image
            finally:
                self.generic_visit(node)

    Visitor().visit(tree)
    return mapping


class Command(BaseCommand):
    help = "Restore ProductModel.image from seed_products.py (match by product name)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite image for all products (seed mapping if available, otherwise fallback by name).",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only set image when it is empty/null.",
        )
        parser.add_argument(
            "--replace-placeholders",
            action="store_true",
            help="Replace known placeholder image URLs (placehold.co / via.placeholder.com).",
        )
        parser.add_argument(
            "--replace-bad-urls",
            action="store_true",
            help="Replace missing/placeholder/source.unsplash.com image URLs.",
        )

    def handle(self, *args, **options):
        force: bool = options["force"]
        only_missing: bool = options["only_missing"]
        replace_placeholders: bool = options["replace_placeholders"]
        replace_bad_urls: bool = options["replace_bad_urls"]

        mapping = _load_seed_name_to_image()
        if not mapping:
            self.stdout.write(self.style.WARNING("No seed image mapping found in seed_products.py"))
            return

        qs = ProductModel.objects.all().order_by("id")
        total = qs.count()
        updated = 0
        unmatched = 0

        with transaction.atomic():
            products = list(qs)
            for p in products:
                current = p.image or ""
                is_missing = not bool(current)
                is_placeholder = ("placehold.co" in current) or ("via.placeholder.com" in current)
                is_bad_url = _is_bad_image_url(current)

                if not force:
                    if only_missing and (not is_missing):
                        continue
                    if replace_placeholders and (not is_placeholder) and (not is_missing):
                        continue
                    if replace_bad_urls and (not is_bad_url):
                        continue

                new_url = mapping.get(p.name)
                if not new_url:
                    new_url = _fallback_image_url(p.name)
                    unmatched += 1

                if new_url != current:
                    p.image = new_url
                    updated += 1

            if updated:
                ProductModel.objects.bulk_update(products, ["image"], batch_size=200)

        self.stdout.write(
            self.style.SUCCESS(
                f"Restored images: updated={updated}/{total}, unmatched_names={unmatched}"
            )
        )
