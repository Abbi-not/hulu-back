"""
apps/market/urls.py
"""

from django.urls import path
from .views import MarketPriceListView

app_name = "market"

urlpatterns = [
    path("", MarketPriceListView.as_view(), name="price-list"),
]
