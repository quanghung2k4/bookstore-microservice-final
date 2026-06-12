from __future__ import annotations

import re
import zlib

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from catalog.infrastructure.models import ProductModel


def _keywords_from_name(name: str) -> str:
    tokens = re.findall(r"[a-zA-Z0-9]+", (name or "").lower())
    # Keep a few meaningful tokens; Unsplash supports comma-separated query.
    tokens = [t for t in tokens if t not in {"pro", "max", "ultra", "new", "edition"}]
    return ",".join(tokens[:4]) or "product"


def _normalize_unsplash_url(url: str, *, width: int, quality: int = 80) -> str:
    # Make sure we always return a stable, direct CDN URL ("link 1") and normalize sizing params.
    if not url.startswith("https://images.unsplash.com/"):
        return url
    sep = "&" if ("?" in url) else "?"
    # `fit=crop` keeps aspect ratio; `auto=format` reduces format issues.
    return f"{url}{sep}auto=format&fit=crop&w={width}&q={quality}"


# Curated direct Unsplash CDN URLs already present in the repo + the user-provided laptop image.
# This avoids calling `source.unsplash.com` (often returns 503 in containers).
CURATED = [
    # user-provided (good direct link)
    ("https://images.unsplash.com/photo-1517336714731-489689fd1ca8", {"laptop", "macbook", "computer", "keyboard"}),

    # from seed_products.py (direct Unsplash links)
    ("https://images.unsplash.com/photo-1584308666744-24d5c474f2ae", {"vitamin", "supplement", "pills", "health"}),
    ("https://images.unsplash.com/photo-1550572017-edd951b55104", {"omega", "fish", "oil", "supplement", "health"}),
    ("https://images.unsplash.com/photo-1559591937-abc8a8b8b8b8", {"toothbrush", "dental", "hygiene", "bath"}),
    ("https://images.unsplash.com/photo-1611996575749-79a3a250f948", {"monopoly", "board", "game", "table"}),
    ("https://images.unsplash.com/photo-1632501641765-e568d28b0015", {"scrabble", "board", "game", "tiles"}),
    ("https://images.unsplash.com/photo-1608889175123-8ee362201f81", {"figure", "toy", "collectible", "action"}),
    ("https://images.unsplash.com/photo-1558618666-fcd25c85cd64", {"tire", "tyre", "car", "automotive", "wheel"}),
    ("https://images.unsplash.com/photo-1609592806596-b8d7a49f4a8a", {"battery", "car", "automotive", "engine"}),
    ("https://images.unsplash.com/photo-1607860108855-64acf2078ed9", {"car", "care", "wax", "cleaning", "detail"}),
    ("https://images.unsplash.com/photo-1621939514649-280e2ee25f60", {"chocolate", "snack", "wafer", "kitkat"}),
    ("https://images.unsplash.com/photo-1559056199-641a0ac8b55e", {"coffee", "nescafe", "drink", "beverage"}),
    ("https://images.unsplash.com/photo-1571091718767-18b5b1457add", {"milo", "drink", "beverage", "cocoa"}),
    ("https://images.unsplash.com/photo-1569718212165-3a8278d5f624", {"noodles", "food", "snack", "maggi"}),
    ("https://images.unsplash.com/photo-1548839140-29a749e1cf4d", {"water", "bottle", "beverage"}),
    ("https://images.unsplash.com/photo-1517093157656-b9eccef91cb1", {"cereal", "breakfast", "cheerios", "food"}),
    ("https://images.unsplash.com/photo-1589924691995-400dc9ecc119", {"dog", "food", "pet", "kibble"}),
    ("https://images.unsplash.com/photo-1601758124510-52d02ddb7cbd", {"dog", "treat", "pet", "dental"}),
    ("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba", {"cat", "pet", "toy"}),
    ("https://images.unsplash.com/photo-1587300003388-59208cc962cb", {"dog", "toy", "rope", "pet"}),
    ("https://images.unsplash.com/photo-1548199973-03cce0bbc87b", {"grooming", "pet", "brush", "fur"}),
]


def _pick_curated_url(*, name: str, width: int) -> str:
    tokens = set(re.findall(r"[a-zA-Z0-9]+", (name or "").lower()))
    scored: list[tuple[int, str]] = []
    for base_url, tags in CURATED:
        score = len(tokens & tags)
        scored.append((score, base_url))

    best = max(s for s, _ in scored) if scored else 0
    candidates = [u for s, u in scored if s == best] if best > 0 else [u for _, u in scored]

    idx = zlib.crc32((name or "").encode("utf-8")) % max(1, len(candidates))
    chosen = candidates[idx]
    return _normalize_unsplash_url(chosen, width=width)


class Command(BaseCommand):
    help = (
        "Set ProductModel.image to a direct Unsplash CDN URL (images.unsplash.com) "
        "based on product name keywords."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--width",
            type=int,
            default=800,
            help="Image width to request from Unsplash resolver.",
        )
        parser.add_argument(
            "--height",
            type=int,
            default=600,
            help="Image height to request from Unsplash resolver.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=8,
            help="Unused in curated mode (kept for backward CLI compatibility).",
        )
        parser.add_argument(
            "--mode",
            type=str,
            default="curated",
            choices=["curated"],
            help="How to select images. 'curated' uses direct images.unsplash.com URLs without network calls.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of products to process (0 = all).",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only set image when it is empty/null.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing image URLs.",
        )

    def handle(self, *args, **options):
        width: int = options["width"]
        height: int = options["height"]
        timeout: int = options["timeout"]
        mode: str = options["mode"]
        limit: int = options["limit"]
        only_missing: bool = options["only_missing"]
        force: bool = options["force"]

        qs = ProductModel.objects.all().order_by("id")
        if only_missing and (not force):
            qs = qs.filter(Q(image__isnull=True) | Q(image=""))
        if limit and limit > 0:
            qs = qs[:limit]

        products = list(qs)
        total = len(products)
        if total == 0:
            self.stdout.write(self.style.WARNING("No products to update"))
            return

        updated = 0
        failed = 0
        to_update: list[ProductModel] = []

        with transaction.atomic():
            for p in products:
                if (not force) and (not only_missing) and p.image:
                    # If user didn't ask to force and not only_missing mode, keep existing.
                    continue
                if only_missing and p.image:
                    continue

                query = _keywords_from_name(p.name)
                _ = query
                _ = height
                _ = timeout
                if mode == "curated":
                    direct = _pick_curated_url(name=p.name, width=width)
                else:
                    direct = None

                if not direct:
                    failed += 1
                    continue

                if p.image != direct:
                    p.image = direct
                    updated += 1
                    to_update.append(p)

            if to_update:
                ProductModel.objects.bulk_update(to_update, ["image"], batch_size=200)

        self.stdout.write(
            self.style.SUCCESS(
                f"Unsplash images updated: updated={updated}/{total}, failed={failed}, force={force}, only_missing={only_missing}"
            )
        )
