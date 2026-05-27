"""
apps/market/urls.py
"""

from django.urls import path
from .views import MarketPriceListView, MarketFiltersView

app_name = "market"

urlpatterns = [
    path("",         MarketPriceListView.as_view(), name="price-list"),
    path("filters/", MarketFiltersView.as_view(),   name="filters"),
]
