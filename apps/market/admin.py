"""
apps/market/admin.py
"""

from django.contrib import admin
from .models import Commodity, MarketPrice


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    list_display  = ["name", "slug", "unit", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_filter   = ["is_active"]


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display  = ["commodity", "price", "change", "market", "country", "recorded_at", "source"]
    list_filter   = ["commodity", "country"]
    search_fields = ["commodity__name", "market", "country"]
    ordering      = ["-recorded_at"]
    date_hierarchy = "recorded_at"