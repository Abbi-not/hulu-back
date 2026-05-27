"""
apps/market/models.py
─────────────────────
Stores commodity price snapshots.

Each MarketPrice row represents the latest known price for one
commodity in one market/region. The API view reads from this table;
prices can be updated by an admin, a management command, or a future
data-pipeline task.
"""

from django.db import models
from django.utils import timezone


class Commodity(models.Model):
    """Master list of tradeable crops."""
    name        = models.CharField(max_length=100, unique=True)   # "Teff"
    slug        = models.SlugField(max_length=120, unique=True)   # "teff"
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, blank=True, help_text="Emoji icon")
    unit        = models.CharField(max_length=50, default="per quintal")
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table  = "market_commodities"
        ordering  = ["name"]
        verbose_name_plural = "commodities"

    def __str__(self):
        return self.name


class MarketPrice(models.Model):
    """
    One price snapshot per commodity per market.
    The latest row per commodity (ordered by -recorded_at) is the
    "current" price the API returns.
    """
    commodity    = models.ForeignKey(
        Commodity, on_delete=models.CASCADE, related_name="prices"
    )
    # Optional market/region tag ("Addis Ababa", "Hawassa", …)
    market       = models.CharField(max_length=120, blank=True, default="")
    country      = models.CharField(max_length=100, blank=True, default="Ethiopia")

    price        = models.DecimalField(max_digits=12, decimal_places=2)
    # Birr change vs previous snapshot
    change       = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    recorded_at  = models.DateTimeField(default=timezone.now, db_index=True)
    source       = models.CharField(max_length=200, blank=True)   # "ECX", "CSO", …

    class Meta:
        db_table = "market_prices"
        ordering = ["-recorded_at"]
        indexes  = [
            models.Index(fields=["commodity", "-recorded_at"]),
            models.Index(fields=["country", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.commodity.name} @ {self.price} ({self.recorded_at.date()})"

    @property
    def change_percent(self) -> float:
        """% change relative to the previous price snapshot."""
        prev = float(self.price) - float(self.change)
        if prev == 0:
            return 0.0
        return round(float(self.change) / prev * 100, 2)