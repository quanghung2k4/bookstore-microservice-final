from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db.models import Q

from catalog.infrastructure.models import ProductModel


class Command(BaseCommand):
    help = "Set ProductModel.image to a given URL for all products (optionally only missing)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            required=True,
            type=str,
            help="Image URL to assign to products.",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only set image when it is empty/null.",
        )

    def handle(self, *args, **options):
        url: str = options["url"].strip()
        only_missing: bool = options["only_missing"]

        if not url:
            raise CommandError("--url must be a non-empty string")

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError as e:
            raise CommandError(f"Invalid URL provided: {e}")

        qs = ProductModel.objects.all()
        total = qs.count()

        if only_missing:
            qs = qs.filter(Q(image__isnull=True) | Q(image=""))

        updated = qs.update(image=url)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated product images: updated={updated}, total={total}, only_missing={only_missing}"
            )
        )
