"""
apps/market/management/commands/seed_market_prices.py
──────────────────────────────────────────────────────
Populates the DB with initial commodity prices so the API returns
real rows instead of the hardcoded fallback.

Usage:
    python manage.py seed_market_prices
    python manage.py seed_market_prices --clear   # wipe existing prices first
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.market.models import Commodity, MarketPrice


SEED = [
    {"name": "Maize",   "icon": "🌽", "price": 2450, "change": 120},
    {"name": "Wheat",   "icon": "🌾", "price": 3100, "change":  60},
    {"name": "Teff",    "icon": "🌿", "price": 5200, "change": -160},
    {"name": "Beans",   "icon": "🫘", "price": 4800, "change":  50},
    {"name": "Barley",  "icon": "🌱", "price": 2100, "change": -42},
    {"name": "Sorghum", "icon": "🌾", "price": 1950, "change":  78},
]


class Command(BaseCommand):
    help = "Seed initial commodity market prices"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear", action="store_true",
            help="Delete all existing MarketPrice rows before seeding"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = MarketPrice.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing price rows."))

        now = timezone.now()
        created_count = 0

        for item in SEED:
            commodity, _ = Commodity.objects.get_or_create(
                name=item["name"],
                defaults={
                    "slug":    slugify(item["name"]),
                    "icon":    item["icon"],
                    "unit":    "per quintal",
                    "is_active": True,
                }
            )

            # Only insert a new row if there's no recent price (last 24 h)
            recent_cutoff = now - timezone.timedelta(hours=24)
            if not MarketPrice.objects.filter(commodity=commodity, recorded_at__gte=recent_cutoff).exists():
                MarketPrice.objects.create(
                    commodity=commodity,
                    price=item["price"],
                    change=item["change"],
                    market="Addis Ababa",
                    country="Ethiopia",
                    recorded_at=now,
                    source="seed",
                )
                created_count += 1
                self.stdout.write(f"  ✓ {commodity.name}: {item['price']} Br")
            else:
                self.stdout.write(f"  – {commodity.name}: recent price exists, skipped")

        self.stdout.write(self.style.SUCCESS(f"\nDone. {created_count} price row(s) created."))