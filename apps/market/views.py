"""
apps/market/views.py
────────────────────
GET /api/v1/market/          → latest price per active commodity
GET /api/v1/market/?country=Ethiopia  → same, filtered by country

The view returns the most recent MarketPrice row for each active
Commodity. If no rows exist yet (fresh DB), it returns the hardcoded
seed data so the frontend always gets something useful.
"""

from django.db.models import OuterRef, Subquery
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Commodity, MarketPrice
from .serializers import MarketPriceSerializer


# ── Seed data (used only when the DB has no prices yet) ───────────────────────
SEED_PRICES = [
    {"name": "Maize",   "price": 2450, "change": 120,  "unit": "per quintal", "icon": "🌽"},
    {"name": "Wheat",   "price": 3100, "change": 60,   "unit": "per quintal", "icon": "🌾"},
    {"name": "Teff",    "price": 5200, "change": -160, "unit": "per quintal", "icon": "🌿"},
    {"name": "Beans",   "price": 4800, "change": 50,   "unit": "per quintal", "icon": "🫘"},
    {"name": "Barley",  "price": 2100, "change": -42,  "unit": "per quintal", "icon": "🌱"},
    {"name": "Sorghum", "price": 1950, "change": 78,   "unit": "per quintal", "icon": "🌾"},
]

def _seed_response():
    """Return seed prices with computed changePercent."""
    items = []
    for s in SEED_PRICES:
        prev = s["price"] - s["change"]
        pct  = round(s["change"] / prev * 100, 2) if prev else 0
        items.append({
            "name":          s["name"],
            "unit":          s["unit"],
            "icon":          s["icon"],
            "price":         s["price"],
            "change":        s["change"],
            "changePercent": pct,
            "market":        "Addis Ababa",
            "country":       "Ethiopia",
            "recorded_at":   None,
            "source":        "seed",
        })
    return items


class MarketPriceListView(APIView):
    """
    Returns the latest price snapshot for every active commodity.

    Query params
    ─────────────
    country  – filter by country name (case-insensitive, optional)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        country = request.query_params.get("country", "").strip()

        # Sub-query: latest recorded_at per commodity (+ country if given)
        latest_qs = (
            MarketPrice.objects
            .filter(commodity=OuterRef("commodity"))
        )
        if country:
            latest_qs = latest_qs.filter(country__iexact=country)

        latest_qs = latest_qs.order_by("-recorded_at").values("id")[:1]

        prices_qs = (
            MarketPrice.objects
            .filter(id__in=Subquery(latest_qs))
            .select_related("commodity")
            .filter(commodity__is_active=True)
        )

        if not prices_qs.exists():
            # Fall back to seed data so the UI always renders
            return Response(_seed_response())

        serializer = MarketPriceSerializer(prices_qs, many=True)
        return Response(serializer.data)